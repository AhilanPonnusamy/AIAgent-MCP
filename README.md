AIAgent-MCP: Local Agentic AI with Tool Use

Welcome to AIAgent-MCP, a fully local agentic AI experience powered by ollama, uvx, and streamlit! This guide walks you through setting up and running the agent that uses tools like time, ainews, and fetch.

🚀 Clone the Repository

git clone https://github.com/AhilanPonnusamy/AIAgent-MCP.git
cd AIAgent-MCP

🧪 Create and Activate a Virtual Environment

Use Python 3.11 and the following naming convention to avoid updating configs manually.

python3.11 -m venv mcplatest-venv
source mcplatest-venv/bin/activate

🔁 Start the Ollama Server and Model

Run the Gemma 3 12B model locally using Ollama:

ollama run gemma3:12b

⚙️ Start the MCPO Tool Server

uvx mcpo --config config.json --port 8001

Access Tool Endpoint: http://localhost:8001/ainews/docs

🧠 Start the Agent (Client)

In a new terminal (inside virtual environment):

source mcplatest-venv/bin/activate
uvicorn agentic_client:app --reload --port 8000

🖥️ Start the Streamlit UI

In another terminal (also inside virtual environment):

source mcplatest-venv/bin/activate
streamlit run app-ui.py

💡 Example Prompts to Try

Start chatting from the Streamlit UI!

"What is the distance to the moon?"

"What is the current time?" → Should trigger the time tool.

"Can you get latest AI news?" → Should trigger ainews tool and return top 10 articles.

"Can you summarize this article for me: Efficient Fine-Tuning of Language Models with Low-Rank Adapters - https://arxiv.org/abs/2405.16746?" → Should invoke fetch tool and return a nice summary.

🛠️ Troubleshooting

Due to the nature of low precision quantized models, behavior may sometimes be inconsistent. When in doubt:

ollama stop

Then restart your model and servers — things should be back to normal!

🎉 Have Fun!

This project is your sandbox for building powerful local agentic systems with reasoning and tool-usage capabilities. Extend, explore, and enjoy! 😄


