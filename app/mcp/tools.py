# EDUCATIONAL NOTE:
# This file defines the actual logic for our MCP Tools.
# Think of these as the actual "hands" of the AI.
# Instead of being directly bound to LangChain (like in app/tools/),
# they are kept purely as Python functions here. We will register them
# to the MCP Server in server.py.

import os
from typing import Dict, Any

# We can reuse the logic from our existing tools by calling their underlying functions.
# Our existing LangChain tools are decorated with @tool, which turns them into objects.
# We access the raw python function using `.func` (or we can just reimplement simple logic here to keep MCP isolated).

from app.tools.calculator import add, subtract, multiply, divide
from app.tools.weather import get_weather

def mcp_add(a: float, b: float) -> float:
    """Adds two numbers."""
    return add.func(a, b)

def mcp_subtract(a: float, b: float) -> float:
    """Subtracts number b from number a."""
    return subtract.func(a, b)

def mcp_get_weather(location: str) -> str:
    """Returns the weather for a given location."""
    return get_weather.func(location)

def mcp_search_documents(query: str) -> str:
    """
    Searches the uploaded company documents for the given query.
    
    EDUCATIONAL NOTE:
    Here we demonstrate how an MCP tool can access internal business logic, 
    like our RAG vector store, and expose it as a standardized tool.
    """
    # Import inside function to avoid circular dependencies if any
    from app.rag.vectorstore import get_vectorstore
    
    try:
        vs = get_vectorstore()
        docs = vs.similarity_search(query, k=2)
        if not docs:
            return "No relevant documents found."
        
        context = [f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs]
        return "\n\n---\n\n".join(context)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

def mcp_app_info() -> Dict[str, Any]:
    """Returns current application configuration and status."""
    return {
        "app_name": "Company AI Assistant",
        "version": "1.0",
        "mcp_enabled": True,
        "environment": os.environ.get("ENV", "development")
    }
