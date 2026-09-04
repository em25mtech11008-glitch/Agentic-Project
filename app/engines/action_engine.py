"""
==================================================
ACTION ENGINE — Central AI Action Executor
==================================================

Educational Comment:
The core problem with AI chatbots is they "hallucinate" actions (e.g. "I have emailed the customer").
The Action Engine fixes this. When an AI agent decides to do something, it MUST
create a structured Action record here.
If `requires_approval` is True, it goes to the Approval Engine and waits for a human.
Only when approved (or if no approval needed), does the Action Engine actually
call the real system (MongoDB, Stripe, Slack, etc.).
"""

import uuid
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.engines.audit_service import log_activity

load_dotenv(override=True)

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


async def create_action(
    organization_id: str,
    created_by: str,       # 'ai_coo' or 'finance_agent', etc.
    action_type: str,      # e.g., 'SEND_EMAIL', 'CREATE_INVOICE'
    target: dict,          # {"type": "CUSTOMER", "id": "123"}
    payload: dict,         # The data for the action (e.g., email body)
    requires_approval: bool = True
):
    """
    Creates a new pending action.
    """
    db = _get_db()
    action_id = str(uuid.uuid4())
    
    action = {
        "_id": action_id,
        "organization_id": organization_id,
        "created_by": created_by,
        "action_type": action_type,
        "target": target,
        "payload": payload,
        "status": "APPROVAL_REQUIRED" if requires_approval else "PENDING",
        "requires_approval": requires_approval,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.ai_actions.insert_one(action)
    
    await log_activity(
        organization_id, created_by, "AGENT", "ACTION_PREPARED", 
        action_type, "SUCCESS", {"action_id": action_id}
    )
    
    # If it doesn't need approval, we could execute it immediately here.
    # For MVP, we will assume everything is manual or handled by a cron/worker.
    
    return action_id


async def execute_action(action_id: str, executor_user_id: str):
    """
    Actually performs the business logic of an action.
    This is where the system connects to external APIs or mutates the DB.
    """
    db = _get_db()
    
    # 1. Fetch the action
    action = await db.ai_actions.find_one({"_id": action_id})
    if not action:
        raise ValueError("Action not found")
        
    if action["status"] not in ["APPROVED", "PENDING"]:
        raise ValueError(f"Cannot execute action in status: {action['status']}")
        
    # 2. Mark as executing
    await db.ai_actions.update_one(
        {"_id": action_id},
        {"$set": {"status": "EXECUTING", "updated_at": datetime.now(timezone.utc)}}
    )
    
    try:
        # ==========================================================
        # REAL INTEGRATION MOCKUP 
        # ==========================================================
        # In a full system, this would be a massive switch statement routing
        # to external APIs (Stripe, HubSpot, etc.). For our MVP, we update MongoDB.
        
        result = {}
        action_type = action["action_type"]
        payload = action["payload"]
        
        if action_type == "UPDATE_CRM":
            # Example: Update a lead status
            await db.leads.update_one(
                {"_id": action["target"]["id"]},
                {"$set": payload}
            )
            result = {"message": "CRM updated successfully"}
            
        elif action_type == "CREATE_TASK":
            task_id = str(uuid.uuid4())
            new_task = {
                "_id": task_id,
                "organization_id": action["organization_id"],
                "created_at": datetime.now(timezone.utc),
                **payload
            }
            await db.tasks.insert_one(new_task)
            result = {"task_id": task_id, "message": "Task created"}
            
        else:
            # Fallback for demo
            result = {"message": f"Simulated execution of {action_type} (DEMO MODE)"}
            
        # ==========================================================

        # 3. Mark as completed
        await db.ai_actions.update_one(
            {"_id": action_id},
            {
                "$set": {
                    "status": "COMPLETED",
                    "result": result,
                    "executed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        await log_activity(
            action["organization_id"], executor_user_id, "USER", "ACTION_EXECUTED", 
            action_type, "SUCCESS", {"action_id": action_id, "result": result}
        )
        
        return result
        
    except Exception as e:
        # 4. Handle failure
        await db.ai_actions.update_one(
            {"_id": action_id},
            {
                "$set": {
                    "status": "FAILED",
                    "error": str(e),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        await log_activity(
            action["organization_id"], executor_user_id, "USER", "ACTION_FAILED", 
            action_type, "ERROR", {"action_id": action_id, "error": str(e)}
        )
        raise e
