# Company AI Assistant

A full-stack, AI-powered company assistant built with **FastAPI**, **LangChain**, **LangGraph**, and the **Model Context Protocol (MCP)**. 

This repository serves two purposes:
1. A functional AI assistant featuring RAG, Tool Calling, and Web UI.
2. A hands-on **MCP Learning Project** demonstrating how to build MCP Servers, connect MCP Clients, and integrate them into a LangGraph state machine.

## Features

- **Interactive Chat Interface**: A clean, vanilla HTML/JS frontend styled with modern CSS. Conversations are isolated per-tab using unique client-side thread IDs.
- **Google Gemini Integration**: Utilizes `gemini-3.5-flash` for the primary LLM reasoning and response generation, and `gemini-embedding-2` for text embeddings.
- **RAG (Retrieval-Augmented Generation)**: Upload PDFs directly through the UI. The documents are chunked and ingested into a local ChromaDB vector store.
- **Model Context Protocol (MCP)**: Implements an official MCP Server that exposes Tools (MongoDB Querying, Calculator, Weather), Resources (Config, RAG metadata), and Prompts. The LangGraph agent uses `langchain-mcp-adapters` to dynamically bind these tools over a local `stdio` transport.
- **Multi-Agent Supervisor**: Uses LangGraph to orchestrate an AI Workforce. An "AI COO" dynamically routes tasks to 7 specialized virtual employees (Finance, Sales, HR, etc.) based on the user's business intent.
- **Stateful Memory**: Employs LangGraph's `MemorySaver` checkpointer to maintain continuous conversation history.
- **Dashboard Modules**: Full UI panels for each business domain:
  - **Work Inbox**: A unified dashboard showing your active operational tasks and pending high-stakes approvals.
  - **Approvals**: A dedicated queue for reviewing, rejecting, or approving sensitive AI actions (e.g., financial transactions).
  - **Support**: Manage customer inquiries and low-score reviews.
  - **Operations**: Monitor internal workflows, active tasks, and operational priorities.
  - **HR**: Manage the company's employee directory and department structures.
  - **Sales & Finance**: View sales pipelines, leads, overdue invoices, and expense reports.

## Project Structure

```
company-ai-assistant/
├── .env                      # Environment variables (GEMINI_API_KEY, MONGODB_URI)
├── .venv/                    # Python virtual environment
├── data/                     # Directory for storing uploaded PDF files
├── scratch/                  # Utility scripts (DB seeding, testing)
│   └── seed_mongodb.py       # Generates synthetic enterprise data in MongoDB
├── app/
│   ├── main.py               # FastAPI application and route definitions
│   ├── graph/                # LangGraph Multi-Agent Orchestration
│   │   ├── agents.py         # AI Workforce personas (COO + 7 specialists)
│   │   ├── nodes.py          # Graph nodes (Supervisor, Worker, Tools)
│   │   ├── state.py          # State definitions for LangGraph
│   │   └── workflow.py       # State machine compilation
│   ├── models/
│   │   └── llm.py            # ChatGoogleGenerativeAI model initialization
│   ├── mcp/                  # Model Context Protocol Implementation
│   │   ├── server.py         # FastMCP Server (central tool registry)
│   │   ├── client.py         # MCP Client session utility
│   │   ├── mongodb_tools.py  # Raw MongoDB query tools (schema + find)
│   │   ├── enterprise_tools.py # Specialized agent tools (Finance, Sales, HR, Ops, etc.)
│   │   ├── tools.py          # General-purpose MCP Tools
│   │   ├── resources.py      # MCP Resources
│   │   └── prompts.py        # MCP Prompts
│   ├── rag/                  # RAG components
│   │   ├── embeddings.py     # Gemini embeddings configuration
│   │   ├── loader.py         # PDF parsing and document loading
│   │   ├── splitter.py       # Text chunking logic
│   │   └── vectorstore.py    # ChromaDB integration
│   ├── tools/                # Native backend logic (wrapped by MCP)
│   │   ├── calculator.py     # Math operations
│   │   └── weather.py        # Weather lookup
│   └── static/               # Frontend assets
│       ├── index.html        # Main UI
│       └── style.css         # UI Styling
├── docs/mcp/                 # 📚 Comprehensive MCP Learning Hub
├── META-SKILLS.md            # Required skills for developers
└── Rule.md                   # Development guidelines and rules
```

## Setup & Installation

1. **Virtual Environment**: Ensure your virtual environment is set up and activated.
   ```bash
   cd company-ai-assistant
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Dependencies**: Make sure required packages are installed. You will need libraries such as `fastapi`, `uvicorn`, `langchain`, `langchain-google-genai`, `langgraph`, `chromadb`, `pypdf`, `python-dotenv`, `mcp`, `langchain-mcp-adapters`, `motor`, and `pymongo`.

3. **Environment Configuration**: Create or edit the `.env` file in the project root to include your Gemini API key and MongoDB Atlas URI:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
   ```

4. **Seed Database (Optional)**: If you want to populate your MongoDB with synthetic enterprise data, run the seeder script:
   ```bash
   .\.venv\Scripts\python scratch\seed_mongodb.py
   ```

## Usage

1. **Start the Backend Server**:
   ```bash
   .\.venv\Scripts\uvicorn app.main:app --reload
   ```

2. **Access the App**:
   Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. **Interacting**:
   - Type questions in the chat box.
   - Upload PDF files by dragging and dropping them into the upload zone or clicking to browse.
   - Click "Clear History" to reset the current thread.

## Configuration & Customization

- **Model Selection**: To switch models, modify `app/models/llm.py` and update the `model` parameter inside `ChatGoogleGenerativeAI`.
- **Embedding Settings**: Embedding parameters can be configured in `app/rag/embeddings.py`.
- **System Instructions**: You can modify the distinct personas and workflows of the 8 specialized agents inside `app/graph/agents.py`.

## MCP Learning Resources

If you want to learn MCP, start by reading the **[MCP Learning Roadmap](docs/mcp/README.md)**.
