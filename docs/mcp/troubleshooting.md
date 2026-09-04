# MCP Troubleshooting & Security

Integrating an MCP Server introduces an external dependency layer. Here is how to debug issues and secure your architecture.

## Common Mistakes & Troubleshooting

### 1. `stdio` Connection Hangs
If your LangGraph application freezes during startup, the MCP server might be stuck or waiting for input.
**Fix**: Ensure your MCP server script does not have blocking calls, `input()` statements, or infinite loops before initializing the transport.

### 2. Tool Not Found
If the AI tries to call a tool but fails, verify that:
1. The tool is actually decorated with `@mcp.tool()` on the server.
2. The LangChain agent properly loaded the tools via `load_mcp_tools`.
3. The model supports function calling (Gemini Flash/Pro models do).

### 3. Dependency Conflicts
The `mcp` SDK relies on `anyio`, `pydantic`, and `starlette`. If you have conflicting versions (e.g., an outdated `fastapi` installation), the server might fail to start.
**Fix**: Check `pip list` and ensure `pydantic >= 2.0` and `fastapi >= 0.100`.

## Security Considerations

### Authentication & Authorization
By default, a local `stdio` server does not require authentication because it is spawned by the host process (LangGraph) under the same user privileges. 
If you switch to a remote **SSE/HTTP** server, you **MUST** implement authentication (e.g., Bearer tokens in headers) to prevent unauthorized execution of your tools.

### Principle of Least Privilege
**Never expose destructive tools** (e.g., `delete_database`, `execute_arbitrary_code`) unless absolutely necessary and heavily sandboxed.

### Preventing Prompt Injection
Data returned from MCP Tools and Resources is inserted directly into the AI's context window. An attacker could potentially store malicious instructions in a database, which the MCP tool retrieves and feeds to the AI.
**Fix**: Treat all data retrieved via MCP as untrusted user input. Instruct the system prompt to ignore instructions found within retrieved data.
