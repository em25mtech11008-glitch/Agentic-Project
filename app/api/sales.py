"""
==================================================
SALES API — CRM, Leads, Deals
==================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/sales", tags=["Sales"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/leads")
async def list_leads(user: dict = Depends(require_permission("sales.view"))):
    # Fallback to customers collection as "leads" if leads collection is empty 
    # since our seed data creates customers, but we might not have generated explicit leads yet.
    db = _get_db()
    org_id = user["org"]
    
    cursor = db.leads.find({"organization_id": org_id}).limit(100)
    leads = await cursor.to_list(length=100)
    
    for l in leads:
        if "_id" in l:
            l["id"] = str(l["_id"])
            del l["_id"]
            
    return {"leads": leads}
