# AIAgent-MCP: Agentic AI App with MCP and OpenAPI Integration

This project demonstrates a lightweight agentic AI system powered by a quantized `gemma3:12b` model running on Ollama, with tool integration via the MCP server. The goal is to test tool-augmented reasoning like fetching current time, summarizing articles, or retrieving the latest AI news.

---

## 🚀 Getting Started

### 1. Clone the Git Repository

```bash
git clone https://github.com/AhilanPonnusamy/AIAgent-MCP.git
cd AIAgent-MCP
```
### 2. Create and Activate a Virtual Environment

Use Python 3.11 and the following naming convention to avoid updating configs manually.
```bash
python3.11 -m venv mcplatest-venv
source mcplatest-venv/bin/activate
```
### 3. Start the Ollama Server and Model

Run the Gemma 3 12B model locally using Ollama:
```bash
ollama run gemma3:12b
```
### 4. Start the MCPO Tool Server
```bash
uvx mcpo --config config.json --port 8001
```
Access Tool Endpoint: http://localhost:8001/ainews/docs

### 5. Start the Agent (Client)

In a new terminal (inside virtual environment):
```bash
source mcplatest-venv/bin/activate
uvicorn agentic_client:app --reload --port 8000
```
### 6. Start the Streamlit UI

In another terminal (also inside virtual environment):
```bash
source mcplatest-venv/bin/activate
streamlit run app-ui.py
```
## Example Prompts to Try

Start chatting from the Streamlit UI!

#### "What is the distance to the moon?"

#### "What is the current time?" → Should trigger the time tool.

#### "Can you get latest AI news?" → Should trigger ainews tool and return top 10 articles.

#### "Can you summarize this article for me: Efficient Fine-Tuning of Language Models with Low-Rank Adapters - https://arxiv.org/abs/2405.16746?" → Should invoke fetch tool and return a nice summary.

>[!WARNING]
> Due to the nature of low precision quantized models, behavior may sometimes be inconsistent. When in doubt: restart servers and LLM (ollama stop)
> things should be back to normal!

🎉 Have Fun!

This project is your sandbox for building powerful local agentic systems with reasoning and tool-usage capabilities. Extend, explore, and enjoy! 😄


