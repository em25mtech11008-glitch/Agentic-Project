"""
==================================================
APPROVALS API — High Stakes Actions
==================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.middleware import require_permission
from app.engines.approval_engine import (
    get_pending_approvals,
    approve_action,
    reject_action
)

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

class RejectRequest(BaseModel):
    reason: str

@router.get("/pending")
async def list_pending_approvals(user: dict = Depends(require_permission("approvals.view"))):
    """
    Returns all pending high-stakes actions waiting for manager approval.
    """
    try:
        approvals = await get_pending_approvals(user["org"])
        # Format for JSON serialization
        for a in approvals:
            if "_id" in a:
                a["id"] = str(a["_id"])
                del a["_id"]
        return {"approvals": approvals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{action_id}/approve")
async def api_approve_action(action_id: str, user: dict = Depends(require_permission("approvals.approve"))):
    """
    Approves a high-stakes action and immediately triggers its execution.
    """
    try:
        result = await approve_action(action_id, user["org"], user["user_id"])
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{action_id}/reject")
async def api_reject_action(action_id: str, body: RejectRequest, user: dict = Depends(require_permission("approvals.reject"))):
    """
    Rejects a high-stakes action.
    """
    try:
        result = await reject_action(action_id, user["org"], user["user_id"], body.reason)
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
