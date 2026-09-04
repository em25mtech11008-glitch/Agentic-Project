"""
==================================================
HR API — Employees, Leave, Onboarding
==================================================
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/hr", tags=["HR"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/employees")
async def list_employees(user: dict = Depends(require_permission("hr.view"))):
    db = _get_db()
    org_id = user["org"]
    
    cursor = db.employees.find({"organization_id": org_id}).limit(100)
    employees = await cursor.to_list(length=100)
    
    for e in employees:
        if "_id" in e:
            e["id"] = str(e["_id"])
            del e["_id"]
            
    return {"employees": employees}
