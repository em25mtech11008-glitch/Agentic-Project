"""
==================================================
OPERATIONS API — Tasks, Workflows
==================================================
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission
from app.dependencies import get_db

load_dotenv(override=True)

router = APIRouter(prefix="/api/operations", tags=["Operations"])


@router.get("/tasks")
async def list_tasks(user: dict = Depends(require_permission("operations.view")), db = Depends(get_db)):
    org_id = user["org"]
    
    cursor = db.tasks.find({"organization_id": org_id}).limit(100)
    tasks = await cursor.to_list(length=100)
    
    for t in tasks:
        if "_id" in t:
            t["id"] = str(t["_id"])
            del t["_id"]
            
    return {"tasks": tasks}
