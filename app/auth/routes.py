"""
==================================================
AUTH ROUTES — Registration, Login, Logout, Token Refresh
==================================================

Educational Comment:
These are the public-facing authentication endpoints. They handle:
1. User registration (creates a new org + user)
2. Login (validates credentials, returns JWT tokens)
3. Token refresh (exchanges a refresh token for a new access token)
4. Current user profile (returns the authenticated user's info)

SECURITY NOTES:
- Passwords are NEVER stored in plaintext — only bcrypt hashes.
- The login response includes both an access token (short-lived, 30 min)
  and a refresh token (long-lived, 7 days).
- The frontend stores these tokens and sends the access token with every request.
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from app.auth.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.auth.rbac import Role, get_permissions_for_role
from app.auth.middleware import get_current_user

load_dotenv(override=True)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ==================================================
# MONGODB CONNECTION
# ==================================================
_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]


# ==================================================
# REQUEST/RESPONSE SCHEMAS
# ==================================================
# Educational Comment:
# Pydantic models validate incoming request data and define response shapes.
# FastAPI automatically generates OpenAPI docs from these schemas.

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    organization_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


# ==================================================
# REGISTER
# ==================================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """
    Creates a new organization and its first user (CEO role).
    Returns JWT tokens so the user is immediately logged in.
    """
    db = _get_db()

    # Check if email already exists
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create the organization
    org_id = str(uuid.uuid4())
    org = {
        "_id": org_id,
        "name": body.organization_name,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    await db.organizations.insert_one(org)

    # Create the user with CEO role (first user is always CEO)
    user_id = str(uuid.uuid4())
    user = {
        "_id": user_id,
        "name": body.name,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "role": Role.CEO,
        "organization_id": org_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(user)

    # Educational Comment:
    # We now create a stateful session in MongoDB. This gives us the ability to instantly
    # revoke access (e.g., if a device is lost or an employee is terminated) while still
    # using JWTs for the front-end to pass around easily.
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": user_id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
    }
    await db.sessions.insert_one(session)

    # Generate tokens embedding the new session ID
    access_token = create_access_token(user_id, org_id, Role.CEO, session_id)
    refresh_token = create_refresh_token(user_id, session_id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user_id,
            "name": body.name,
            "email": body.email,
            "role": Role.CEO,
            "organization_id": org_id,
            "permissions": list(get_permissions_for_role(Role.CEO)),
        }
    )


# ==================================================
# LOGIN
# ==================================================

@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    """
    Authenticates a user with email + password.
    Returns JWT access and refresh tokens.
    """
    db = _get_db()

    user = await db.users.find_one({"email": body.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user_id = str(user["_id"])
    org_id = user["organization_id"]
    role = user["role"]

    # Educational Comment:
    # A new session is created every time the user logs in. This inherently supports
    # multiple devices (each device gets a unique session_id in the DB).
    session_id = str(uuid.uuid4())
    session = {
        "_id": session_id,
        "user_id": user_id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
    }
    await db.sessions.insert_one(session)

    access_token = create_access_token(user_id, org_id, role, session_id)
    refresh_token = create_refresh_token(user_id, session_id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": role,
            "organization_id": org_id,
            "permissions": list(get_permissions_for_role(role)),
        }
    )


# ==================================================
# REFRESH TOKEN
# ==================================================

@router.post("/refresh")
async def refresh_token(body: RefreshRequest):
    """
    Exchanges a valid refresh token for a new access token.
    This allows the frontend to maintain sessions without re-login.
    """
    db = _get_db()

    payload = verify_refresh_token(body.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = await db.users.find_one({"_id": payload["sub"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    session_id = payload.get("sid")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing session ID"
        )
        
    # Educational Comment:
    # Validate the session! Even if the JWT signature is valid and it hasn't expired,
    # the session could have been revoked (e.g., user logged out from another device).
    session = await db.sessions.find_one({"_id": session_id, "is_active": True})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or expired"
        )

    user_id = str(user["_id"])
    new_access_token = create_access_token(user_id, user["organization_id"], user["role"], session_id)
    new_refresh_token = create_refresh_token(user_id, session_id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }


# ==================================================
# LOGOUT
# ==================================================

@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """
    Invalidates the current session so the tokens can no longer be used.
    
    Educational Comment:
    Since `get_current_user` extracts the JWT and queries the session, 
    the `user` object passed here contains the `session_id`. We mark it
    `is_active = False` to permanently revoke it in the database.
    """
    db = _get_db()
    session_id = user.get("session_id")
    if session_id:
        await db.sessions.update_one(
            {"_id": session_id},
            {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
        )
    return {"message": "Logged out successfully"}


# ==================================================
# CURRENT USER (ME)
# ==================================================

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    This endpoint is used by the frontend on app load to verify the session.
    """
    return {
        "id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "organization_id": user["org"],
        "permissions": list(get_permissions_for_role(user["role"])),
    }
