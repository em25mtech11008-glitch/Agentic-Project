"""
==================================================
DASHBOARD API — Aggregated metrics
==================================================

Educational Comment:
This API returns high-level metrics for the React frontend dashboards.
In a real application, these aggregations would use MongoDB aggregation pipelines.
"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from app.auth.middleware import require_permission
from app.dependencies import get_db

load_dotenv(override=True)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/")
async def get_dashboard(user: dict = Depends(require_permission("dashboard.view")), db = Depends(get_db)):
    """
    Returns high-level statistics for the dashboard.
    """
    org_id = user["org"]
    
    # Very basic metrics for demo
    customers_count = await db.customers.count_documents({"organization_id": org_id})
    orders_count = await db.orders.count_documents({"organization_id": org_id})
    tasks_count = await db.tasks.count_documents({"organization_id": org_id})
    pending_approvals = await db.ai_actions.count_documents({"organization_id": org_id, "status": "APPROVAL_REQUIRED"})
    
    return {
        "metrics": {
            "customers": customers_count,
            "orders": orders_count,
            "tasks": tasks_count,
            "pending_approvals": pending_approvals
        },
        "role": user["role"]
    }
