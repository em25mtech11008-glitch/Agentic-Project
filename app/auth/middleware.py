"""
==================================================
AUTH MIDDLEWARE — FastAPI Dependencies for Auth + RBAC
==================================================

Educational Comment:
FastAPI uses a dependency injection system. Instead of writing authentication
checks inside every route handler, we define reusable "dependencies" that
automatically run before the handler executes.

HOW IT WORKS:
1. `get_current_user` — Extracts and verifies the JWT from the Authorization header.
   If the token is missing/invalid, it raises 401 Unauthorized immediately.
2. `require_permission("finance.view")` — Returns a dependency that checks if the
   current user's role has the specified permission. If not, raises 403 Forbidden.

USAGE IN ROUTES:
    @router.get("/api/finance/invoices")
    async def get_invoices(user = Depends(require_permission("finance.view"))):
        # 'user' is guaranteed to be authenticated AND authorized
        org_id = user["org"]
        ...
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.auth.auth_utils import verify_access_token
from app.auth.rbac import has_permission

load_dotenv(override=True)

# ==================================================
# HTTP BEARER SCHEME
# ==================================================
# Educational Comment:
# HTTPBearer automatically extracts the token from the "Authorization: Bearer <token>"
# header. If the header is missing, FastAPI returns 401 before our code even runs.

security = HTTPBearer()

# ==================================================
# MONGODB CONNECTION (for user lookups)
# ==================================================
_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


# ==================================================
# CORE AUTH DEPENDENCY
# ==================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency that:
    1. Extracts the JWT from the Authorization header.
    2. Verifies the token signature and expiration.
    3. Looks up the user in the database to get the REAL role
       (never trust the role embedded in the JWT alone).
    4. Returns the user dict if everything checks out.
    5. Raises 401 Unauthorized if anything fails.
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # SECURITY: Always fetch the real user from the DB to get the current role.
    # The JWT role might be stale if an admin changed it after the token was issued.
    db = _get_db()
    user = await db.users.find_one({"_id": payload["sub"]})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Educational Comment:
    # We now validate the session stored in MongoDB on every authenticated request.
    # This guarantees that if a session is revoked (logout), the token instantly fails.
    session_id = payload.get("sid")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing session ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    session = await db.sessions.find_one({"_id": session_id, "is_active": True})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "org": user["organization_id"],
        "session_id": session_id,
    }


# ==================================================
# PERMISSION DEPENDENCY FACTORY
# ==================================================

def require_permission(permission: str):
    """
    Factory function that returns a FastAPI dependency.
    The dependency checks if the current user's role has the specified permission.

    Usage:
        @router.get("/api/finance/invoices")
        async def get_invoices(user = Depends(require_permission("finance.view"))):
            ...
    """
    async def permission_checker(
        user: dict = Depends(get_current_user)
    ) -> dict:
        if not has_permission(user["role"], permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission}' required. Your role '{user['role']}' does not have this permission.",
            )
        return user

    return permission_checker
