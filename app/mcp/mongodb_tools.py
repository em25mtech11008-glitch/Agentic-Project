"""
Educational Comment:
This module contains the MCP tools specifically designed for MongoDB integration.
By separating database tools from general tools, we follow the separation of concerns (Rule 3).
The tools allow the AI Workforce (especially Finance and Sales agents) to dynamically 
discover the structure of the data and execute queries against it.
"""

import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

# We initialize a global Motor client but we won't connect until a tool is called,
# or we can just connect lazily to avoid connection errors if the URI is bad on startup.
_mongo_client = None

def get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri or "<username>" in uri:
            raise ValueError("MONGODB_URI is missing or invalid in .env")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]

def register_mongodb_tools(mcp: FastMCP):
    """
    Registers MongoDB specific tools to the provided MCP server.
    """
    
    @mcp.tool()
    async def get_database_schema() -> str:
        """
        Retrieves the names of all collections in the 'startup_ai' MongoDB database,
        along with a single sample document from each collection.
        This helps the AI understand the data structure before writing queries.
        """
        try:
            db = get_db()
            collections = await db.list_collection_names()
            
            schema_info = {}
            for coll_name in collections:
                # Fetch one document to show the schema
                sample = await db[coll_name].find_one()
                if sample:
                    # Remove the ObjectID as it's not JSON serializable easily by default
                    sample.pop('_id', None)
                schema_info[coll_name] = sample or "Empty Collection"
                
            return json.dumps(schema_info, indent=2, default=str)
        except Exception as e:
            return f"Error fetching database schema: {str(e)}"

    @mcp.tool()
    async def execute_mongo_query(collection_name: str, filter_json: str, limit: int = 10) -> str:
        """
        Executes a read-only find() query against a specific MongoDB collection.
        
        Args:
            collection_name: The name of the collection (e.g., 'customers', 'invoices')
            filter_json: A valid JSON string representing the MongoDB query filter (e.g., '{"status": "Overdue"}')
            limit: Maximum number of records to return (max 50)
        """
        try:
            db = get_db()
            
            # Parse the JSON string back into a Python dict
            try:
                query_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                return "Error: filter_json must be a valid JSON string."
            
            limit = min(limit, 50) # Hard limit for safety and context window
            
            cursor = db[collection_name].find(query_filter).limit(limit)
            results = []
            
            async for document in cursor:
                document.pop('_id', None) # Remove non-serializable ObjectId
                results.append(document)
                
            if not results:
                return "Query returned 0 results."
                
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            return f"Error executing query: {str(e)}"
