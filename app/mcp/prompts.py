# EDUCATIONAL NOTE:
# This file defines MCP Prompts.
# A Prompt provides standardized instructions or context that a client can fetch
# and use to guide the AI's behavior. 

def get_assistant_prompt() -> str:
    """Returns the base system instructions for the company assistant."""
    return """
You are the official Company AI Assistant.
You have access to a variety of tools provided by the Model Context Protocol (MCP).
If the user asks for calculations, use the math tools.
If the user asks for weather, use the weather tool.
If the user asks questions about company documents, use the document search tool or RAG functionality.
Always be polite, professional, and concise.
"""

def get_summarization_prompt() -> str:
    """Returns a prompt specialized for document summarization."""
    return """
Please summarize the following document context.
Focus on extracting the most critical business metrics, action items, and key takeaways.
Ignore boilerplate language and keep the summary under 3 paragraphs.
"""
