"""
==================================================
SUPPORT API — Support Tickets
==================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/support", tags=["Support"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/tickets")
async def list_tickets(user: dict = Depends(require_permission("support.view"))):
    db = _get_db()
    org_id = user["org"]
    
    # In our seed data, we can treat low-scoring reviews as tickets
    cursor = db.reviews.find({"organization_id": org_id, "review_score": {"$lte": 3}}).limit(100)
    tickets = await cursor.to_list(length=100)
    
    for t in tickets:
        if "_id" in t:
            t["id"] = str(t["_id"])
            del t["_id"]
            
    return {"tickets": tickets}
