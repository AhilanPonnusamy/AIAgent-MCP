import streamlit as st
import json
import http.client

# Agent server config
AGENT_API_URL = "localhost:8000"
API_ENDPOINT = "/api/agent"

# Init session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""
if "is_waiting" not in st.session_state:
    st.session_state.is_waiting = False
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Function to contact the backend
def call_agent_api(messages):
    conn = http.client.HTTPConnection(AGENT_API_URL)
    headers = {"Content-type": "application/json"}
    body = json.dumps({"messages": messages})
    try:
        conn.request("POST", API_ENDPOINT, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if response.status == 200:
            return json.loads(data.decode("utf-8")).get("response", "")
        else:
            return f"Error: Agent returned {response.status}"
    except Exception as e:
        return f"Error: {e}"

# Handle message sending
def submit_message():
    user_input = st.session_state.input_text.strip()
    if user_input:
        if user_input.lower() == st.session_state.last_user_input.lower():
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "It seems like you're asking the same thing again. Do you want me to repeat the last response?"
            })
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.is_waiting = True
            st.session_state.last_user_input = user_input
            response = call_agent_api(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        #st.session_state.input_text = ""  # clear input box after processing

# Title
st.title("Agentic Chat Interface")

# Render history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='background-color:#d9eaf7; color:#000; padding:10px; border-radius:10px; margin-bottom:10px'><b>You:</b> {msg['content']}</div>",
            unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='background-color:#fff3cd; color:#000; padding:10px; border-radius:10px; margin-bottom:10px'><b>Agent:</b> {msg['content']}</div>",
            unsafe_allow_html=True)

# Input and submit button
with st.form(key="chat_form", clear_on_submit=False):
    st.text_area("Type your message", key="input_text", height=100)
    submitted = st.form_submit_button("Send")
    if submitted:
        submit_message()
        st.rerun()

# Clear chat button
#if st.button("🧹 Clear Chat"):
#    st.session_state.chat_history = []
#    st.session_state.last_user_input = ""
#    st.session_state.input_text = ""
#    st.rerun()
