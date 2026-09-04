"""
==================================================
AUDIT SERVICE — Immutable Activity Logging
==================================================

Educational Comment:
Every important action in the system must be auditable. This service writes
records to the `audit_logs` MongoDB collection.
Crucially, there is no "update" or "delete" function here — audit logs
are append-only by design for security and compliance.
"""

import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv(override=True)

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


async def log_activity(
    organization_id: str,
    actor_id: str,        # userId or agent name
    actor_type: str,      # 'USER' or 'AGENT'
    action: str,          # e.g., 'APPROVED_ACTION', 'PREPARED_RECOMMENDATION'
    system: str,          # e.g., 'Finance', 'Sales', 'Core'
    result: str = "SUCCESS",
    details: dict = None
):
    """
    Writes an immutable audit log entry.
    """
    db = _get_db()
    
    audit_entry = {
        "_id": str(uuid.uuid4()),
        "organization_id": organization_id,
        "actor_id": actor_id,
        "actor_type": actor_type,
        "action": action,
        "system": system,
        "result": result,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc)
    }
    
    await db.audit_logs.insert_one(audit_entry)
    return audit_entry["_id"]
