# EDUCATIONAL NOTE:
# This file defines MCP Resources.
# A Resource is data that the AI can read. Unlike Tools, Resources do not take arguments
# and are accessed via standard URIs (like config://app or file:///...).
# 
# Think of Resources as providing "context" rather than "action".

import os

def get_company_policy() -> str:
    """
    Returns the general company policy.
    
    EDUCATIONAL NOTE:
    This data is static and provides context to the AI. When the AI reads the
    'policy://general' resource, it will get this text.
    """
    return """
    COMPANY POLICY v1.0
    
    1. Working Hours: Core hours are 10:00 AM to 3:00 PM.
    2. Remote Work: Employees may work remotely up to 3 days a week.
    3. Leave: 20 days of paid time off per year.
    4. Expense Reporting: All expenses must be submitted via the internal portal within 30 days.
    """

def get_rag_metadata() -> str:
    """
    Returns metadata about the currently ingested documents.
    
    EDUCATIONAL NOTE:
    This shows how a resource can expose dynamic system state as static-looking data.
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        return "No documents currently uploaded."
        
    files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    if not files:
        return "No PDF documents currently uploaded."
        
    return f"Currently indexed RAG documents:\n" + "\n".join([f"- {file}" for file in files])
