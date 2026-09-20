import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from app.graph.checkpointer import AsyncMongoDBSaver
from app.graph.workflow import create_workflow

load_dotenv()

# We initialize this once globally so all API routes share the exact same MongoDB Checkpointer
_mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
mongodb_saver = AsyncMongoDBSaver(_mongo_client)

# The global LangGraph application
graph_app = create_workflow(checkpointer=mongodb_saver)

def get_graph_app():
    return graph_app
