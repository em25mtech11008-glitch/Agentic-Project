"""
==================================================
APPROVALS API — High Stakes Actions
==================================================
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/pending")
async def list_pending_approvals(user: dict = Depends(require_permission("approvals.view"))):
    db = _get_db()
    org_id = user["org"]
    
    # In our database, we track pending high-stake actions in the approvals collection
    cursor = db.approvals.find({"organization_id": org_id, "status": "pending"}).limit(100)
    approvals = await cursor.to_list(length=100)
    
    for a in approvals:
        if "_id" in a:
            a["id"] = str(a["_id"])
            del a["_id"]
            
    return {"approvals": approvals}
