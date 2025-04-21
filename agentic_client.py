from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import json
import ollama
import threading
import os
import logging
from datetime import datetime

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list

# Tool endpoints
tool_endpoints = {
    "memory": "http://localhost:8001/memory/memory",
    "time": "http://localhost:8001/time",
    "fetch": "http://localhost:8001/fetch/fetch",
    "ainews": "http://localhost:8001/ainews/latest_genai_news"
}

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

def call_tool_via_http(tool_name, input_data=""):
    if tool_name not in tool_endpoints:
        return f"Tool {tool_name} not configured."

    try:
        if tool_name == "ainews":
            response = requests.post(tool_endpoints[tool_name], json={"input": input_data}, timeout=30)

        elif tool_name == "fetch":
            #response = requests.post(tool_endpoints[tool_name], json={"url": input_data,"max_length": 5000,"start_index": 0,"raw": False}, timeout=30)
                if isinstance(input_data, str):
                 fetch_input = {
                    "url": input_data,
                    "max_length": 5000,
                    "start_index": 0,
                    "raw": False
                 }
                elif isinstance(input_data, dict):
                    fetch_input = {
                        "url": input_data.get("url", ""),
                        "max_length": input_data.get("max_length", 5000),
                        "start_index": input_data.get("start_index", 0),
                        "raw": input_data.get("raw", False)
                      }
                else:
                    return "Invalid input to fetch tool."
 
                try:
                    response = requests.post(tool_endpoints[tool_name], json=fetch_input, timeout=30)

                     # Log response content to console
                    print(f"[Agent Fetch Tool] Response Status: {response.status_code}")
                    print(f"[Agent Fetch Tool] Raw Response: {response.text[:3000]}")  # Only print first 1000 chars

                    response.raise_for_status()
                    #return response.json().get("result", response.text)
                    return response.text
                except Exception as e:
                    print(f"[Agent Fetch Tool] Exception: {str(e)}")  # Log exception as well
                    return f"Error calling fetch: {str(e)}"
       
        elif tool_name == "time":
            if not isinstance(input_data, dict):
                return "Input to 'time' tool must be a dictionary."

            # convert_time call
            if {"source_timezone", "target_timezone", "time"} <= input_data.keys():
                #input_data.setdefault("source_timezone", "America/New_York")
                input_data.setdefault("target_timezone", "America/New_York")
                endpoint = "/convert_time"

            # get_current_time call
            else:
                input_data.setdefault("timezone", "America/New_York")
                endpoint = "/get_current_time"

            response = requests.post(tool_endpoints[tool_name] + endpoint, json=input_data, timeout=30)
            print(f"[Agent Fetch Tool] Response Status: {response.status_code}")
            print(f"[Agent Fetch Tool] Raw Response: {response.text}")  


        else:
            response = requests.post(tool_endpoints[tool_name], json={"input": input_data}, timeout=30)

        response.raise_for_status()
        return response.json().get("result", response.text)

    except Exception as e:
        return f"Error calling {tool_name}: {str(e)}"

@app.post("/api/agent")
async def agent_handler(req: ChatRequest):
    chat_history = req.messages
    log_lines = []

    system_prompt = (
        "You are an intelligent agent with access to the following tools: memory, time, fetch, and ainews. "
        "When a user asks a question, you should first think through your plan and, if needed, issue a tool call using the format: "
        "TOOLCALL[tool_name|input_data]. You will receive the tool result and can continue reasoning based on it.\n\n"

        "When using the 'ainews' tool, your job is to return a high-quality human-readable list of exactly 10 recent AI-related news items, "
        "carefully selected to ensure a balanced distribution — ideally 5 from Medium blogs and 5 from ArXiv preprints or similar sources. "
        "Ensure that each item includes:\n"
        "- A concise headline or summary\n"
        "- A valid, accurate, and complete URL (this is extremely important — users will click on them, so incorrect or missing URLs make the output unusable!)\n"
        "- Keep the order logical or grouped if appropriate (e.g., similar topics or sources)\n\n"

        "URLs must be exactly as returned by the ainews tool — do not rewrite or drop them. If a URL is missing or appears malformed, do not include that item.\n"
        "Treat the correct display of URLs as critical to user experience.\n\n"

        "After displaying the result, store all returned URLs and headlines in memory. "
        "On future calls to ainews, only show items that are new (i.e., not already stored in memory).\n"

        "Use your tools wisely, reason clearly, and avoid hallucinating information or links."
    )


    messages = [{"role": "system", "content": system_prompt}] + chat_history
    final_response = ""

    for round_num in range(3):
        try:
            log_lines.append(f"[Round {round_num+1}] Calling LLM with messages: {json.dumps(messages[-2:], indent=2)}")
            response = ollama.chat(model="gemma3:12b", messages=messages)
            reply = response['message']['content']
            messages.append({"role": "assistant", "content": reply})
            log_lines.append(f"LLM Reply: {reply}")

            if "TOOLCALL[" in reply:
                try:
                    tool_part = reply.split("TOOLCALL[")[1].split("]")[0]
                    tool_name, tool_input = tool_part.split("|", 1)
                    tool_name = tool_name.strip()
                    tool_input = json.loads(tool_input.strip()) if tool_input.strip().startswith("{") else tool_input.strip()
                    tool_result = call_tool_via_http(tool_name, tool_input)
                    log_lines.append(f"Tool Call -> {tool_name} | Input: {tool_input} | Result: {tool_result}")
                    messages.append({"role": "user", "content": f"TOOLRESULT[{tool_result}]"})
                except Exception as e:
                    error_msg = f"Tool call parsing failed: {str(e)}"
                    log_lines.append(f"[ERROR] {error_msg}")
                    messages.append({"role": "user", "content": f"TOOLRESULT[{error_msg}]"})
            else:
                final_response = reply
                break
        except Exception as e:
            final_response = f"Error calling LLM: {str(e)}"
            log_lines.append(f"[ERROR] {final_response}")
            break

    log_filename = datetime.now().strftime("agent-%Y%m%d-%H%M%S.log")
    with open(os.path.join(log_dir, log_filename), "w") as f:
        f.write("\n".join(log_lines))

    return {"response": final_response}
