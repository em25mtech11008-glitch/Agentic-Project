"""
==================================================
FINANCE API — Invoices, Expenses, Payments
==================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/finance", tags=["Finance"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/invoices")
async def list_invoices(user: dict = Depends(require_permission("finance.view"))):
    db = _get_db()
    org_id = user["org"]
    
    cursor = db.invoices.find({"organization_id": org_id}).limit(100)
    invoices = await cursor.to_list(length=100)
    
    for i in invoices:
        if "_id" in i:
            i["id"] = str(i["_id"])
            del i["_id"]
            
    return {"invoices": invoices}


@router.get("/expenses")
async def list_expenses(user: dict = Depends(require_permission("finance.view"))):
    db = _get_db()
    org_id = user["org"]
    
    cursor = db.expenses.find({"organization_id": org_id}).limit(100)
    expenses = await cursor.to_list(length=100)
    
    for e in expenses:
        if "_id" in e:
            e["id"] = str(e["_id"])
            del e["_id"]
            
    return {"expenses": expenses}
