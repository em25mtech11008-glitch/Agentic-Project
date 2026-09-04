"""
==================================================
APPROVAL ENGINE — Human-in-the-Loop Workflow
==================================================

Educational Comment:
When the Action Engine marks an action as `requires_approval=True`, it sits
in the `APPROVAL_REQUIRED` state.
The Approval Engine provides the APIs for human managers to review, edit,
approve, or reject these actions. Once approved, it hands the action back
to the Action Engine for execution.
"""

from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.engines.audit_service import log_activity
from app.engines.action_engine import execute_action

load_dotenv(override=True)

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


async def get_pending_approvals(organization_id: str):
    """
    Fetches all actions waiting for approval in the organization.
    In a real app, this would filter by the user's role (e.g., FINANCE only sees finance approvals).
    """
    db = _get_db()
    cursor = db.ai_actions.find({"organization_id": organization_id, "status": "APPROVAL_REQUIRED"})
    return await cursor.to_list(length=100)


async def approve_action(action_id: str, organization_id: str, approver_user_id: str):
    """
    Approves an action and triggers its execution immediately.
    """
    db = _get_db()
    
    # 1. Verify action exists and needs approval
    action = await db.ai_actions.find_one({"_id": action_id, "organization_id": organization_id})
    if not action:
        raise ValueError("Action not found")
        
    if action["status"] != "APPROVAL_REQUIRED":
        raise ValueError(f"Action cannot be approved. Current status: {action['status']}")
        
    # 2. Mark as approved
    await db.ai_actions.update_one(
        {"_id": action_id},
        {
            "$set": {
                "status": "APPROVED",
                "approved_by": approver_user_id,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # 3. Log the approval
    await log_activity(
        organization_id, approver_user_id, "USER", "ACTION_APPROVED", 
        action["action_type"], "SUCCESS", {"action_id": action_id}
    )
    
    # 4. Execute it
    # We await execution directly for simplicity. In production, this might be sent to a Celery/Redis queue.
    result = await execute_action(action_id, approver_user_id)
    return result


async def reject_action(action_id: str, organization_id: str, rejector_user_id: str, reason: str):
    """
    Rejects an action.
    """
    db = _get_db()
    
    action = await db.ai_actions.find_one({"_id": action_id, "organization_id": organization_id})
    if not action:
        raise ValueError("Action not found")
        
    if action["status"] != "APPROVAL_REQUIRED":
        raise ValueError(f"Action cannot be rejected. Current status: {action['status']}")
        
    await db.ai_actions.update_one(
        {"_id": action_id},
        {
            "$set": {
                "status": "REJECTED",
                "error": f"Rejected by user: {reason}",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    await log_activity(
        organization_id, rejector_user_id, "USER", "ACTION_REJECTED", 
        action["action_type"], "SUCCESS", {"action_id": action_id, "reason": reason}
    )
    
    return {"message": "Action rejected"}
