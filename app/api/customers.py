"""
==================================================
CUSTOMERS API — CRUD operations for customers
==================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission

load_dotenv(override=True)

router = APIRouter(prefix="/api/customers", tags=["Customers"])

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


@router.get("/")
async def list_customers(user: dict = Depends(require_permission("customer.view"))):
    """
    Returns all customers belonging to the user's organization.
    """
    db = _get_db()
    org_id = user["org"]
    
    # Exclude _id to make it easy to serialize, or map it to id
    cursor = db.customers.find({"organization_id": org_id}).limit(100)
    customers = await cursor.to_list(length=100)
    
    # Clean up IDs for JSON serialization
    for c in customers:
        if "_id" in c:
            c["id"] = str(c["_id"])
            del c["_id"]
            
    return {"customers": customers}


@router.get("/{customer_id}")
async def get_customer(customer_id: str, user: dict = Depends(require_permission("customer.view"))):
    """
    Returns a specific customer.
    Ensures the customer belongs to the user's organization (Multi-tenant check).
    """
    db = _get_db()
    org_id = user["org"]
    
    customer = await db.customers.find_one({"_id": customer_id, "organization_id": org_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer["id"] = str(customer["_id"])
    del customer["_id"]
    return customer
