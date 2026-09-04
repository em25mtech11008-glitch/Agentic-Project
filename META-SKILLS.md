# META-SKILLS

This document outlines the core skills required for developers or AI coding agents to successfully maintain and extend the **Company AI Assistant** project. 

## 1. Core Skills
- **Python**: The entire backend and AI logic is written in modern Python.
- **FastAPI**: Required for building the backend server, handling endpoints (`/api/chat`), and processing JSON schemas and file uploads.
- **Async Python (`asyncio`)**: Required for non-blocking I/O, especially when communicating with the MCP subprocess or streaming API responses.
- **REST APIs**: Required to understand the client-server communication between the Vanilla JS frontend and FastAPI backend.

## 2. AI Skills
- **LLM Concepts**: Understanding context windows, prompt injection, and generation parameters.
- **Google Gemini**: The primary underlying model used via `ChatGoogleGenerativeAI`.
- **Function/Tool Calling**: Required to understand how the LLM determines when to execute external logic instead of generating text.
- **Agent Architecture**: Understanding the ReAct (Reason + Act) loop pattern for autonomous problem solving.

## 3. LangChain & LangGraph Skills
- **LangChain Core**: Understanding `BaseMessage`, `ToolMessage`, `SystemMessage`, and `BaseTool`.
- **LangGraph**: Required for managing the state machine.
  - **State**: Defining TypedDict structures to hold message history and context.
  - **Nodes & Edges**: Writing Python functions that update state and conditional functions that route execution.
  - **Checkpointing**: Using `MemorySaver` to persist thread history.

## 4. RAG Skills (Retrieval-Augmented Generation)
- **Document Loading & Chunking**: Using `PyPDFLoader` and `RecursiveCharacterTextSplitter`.
- **Embeddings**: Converting text to vectors using `GoogleGenerativeAIEmbeddings`.
- **Vector Databases**: Managing and querying `ChromaDB`.
- **Context Injection**: Modifying the system prompt dynamically to include retrieved document chunks.

## 5. MCP Skills (Model Context Protocol)
- **MCP Architecture**: Understanding the Client, Server, and Host relationship. This project uses MCP to decouple tool logic from the core AI engine.
- **MCP Servers (`FastMCP`)**: Building servers that expose Tools, Resources, and Prompts.
- **MCP Clients & Adapters**: Using `mcp.client` and `langchain-mcp-adapters` to dynamically load tools into the LangGraph state machine.
- **MCP Transports**: Understanding `stdio` communication for local subprocess servers.
- **JSON-RPC**: The underlying protocol format used by MCP.
