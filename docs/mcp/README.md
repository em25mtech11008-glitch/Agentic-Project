# Model Context Protocol (MCP) Learning Roadmap

Welcome to the **Company AI Assistant's MCP Integration** learning hub! This directory contains documentation designed to take you from a beginner to an advanced understanding of the Model Context Protocol, and how it is integrated into our LangGraph-based AI application.

## What is MCP?
The Model Context Protocol (MCP) is an open standard introduced by Anthropic that standardizes how AI models connect to data sources, tools, and environments. Think of it as a "USB-C plug for AI applications"—a universal way for an AI agent to discover and use capabilities across different systems without writing custom glue code for every integration.

## Learning Roadmap

Follow these documents in order to progressively learn MCP:

### Level 1 — Fundamentals
- [Concepts](concepts.md): What are MCP Tools, Resources, and Prompts?
- [Architecture](architecture.md): Clients, Servers, Hosts, and Transports.

### Level 2 — Implementation & Integration
- [LangGraph Integration](langgraph-integration.md): How our FastAPI/LangGraph backend connects to the local MCP server using `langchain-mcp-adapters`.

### Level 3 — Production & Operations
- [Troubleshooting & Security](troubleshooting.md): Debugging connections, common mistakes, and security best practices.

## Project MCP Structure

Within the main application, the MCP functionality is cleanly isolated:
- `app/mcp/server.py`: The MCP server exposing educational capabilities.
- `app/mcp/client.py`: The MCP client that our LangGraph agent uses to talk to the server.
- `app/mcp/tools.py`, `resources.py`, `prompts.py`: Definitions for the specific primitives.
- `examples/mcp/`: Standalone scripts to experiment with MCP concepts outside of the main web app.

Enjoy your journey into standardizing AI tool usage!
