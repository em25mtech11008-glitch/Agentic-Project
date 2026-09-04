# MCP Concepts

The Model Context Protocol (MCP) revolves around three core primitives that standardizes what an AI can "see" and "do": **Tools**, **Resources**, and **Prompts**.

## 1. Tools

> **"A tool performs an action."**

Tools are functions that the AI can call to perform an action, retrieve dynamic data, or compute a result.
Unlike Resources, Tools usually take arguments (an input schema) and their output often changes based on those arguments.

### MCP Tools vs Native LangChain Tools
- **Native LangChain Tools**: Defined directly in the AI application codebase. Tight coupling.
- **MCP Tools**: Defined on a remote or separate MCP Server. The AI Application (LangGraph) queries the MCP server ("What tools do you have?"), and the server replies with a list of tools and their JSON Schema. The AI can then ask the MCP server to execute one of those tools on its behalf.

*Example*: A `calculator` tool that takes `a` and `b` and returns their sum.

## 2. Resources

> **"A resource provides contextual data."**

Resources are static or semi-static pieces of data that the AI can read. They are conceptually similar to files, databases, or API endpoints, but exposed over a standardized URI structure (`mcp://...`).
They don't take arguments like tools do; they are simply "read".

*Example*: Application configuration data, a list of current employees, or a database schema.

## 3. Prompts

> **"A prompt provides standardized instructions."**

Prompts in MCP allow servers to provide reusable template instructions or context that the AI application can load. This helps standardize how an AI behaves when talking to a specific MCP server.

*Example*: A standard "Code Review" prompt provided by a GitHub MCP Server that includes best practices and guidelines for analyzing PRs.
