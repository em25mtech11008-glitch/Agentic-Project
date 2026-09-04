"""
==================================================
AUTH UTILITIES — Password Hashing & JWT Management
==================================================

Educational Comment:
This module handles the cryptographic operations for authentication:
1. Password hashing with bcrypt (one-way hash — we can never recover the original).
2. JWT token creation and verification (stateless auth — no server-side sessions needed).

WHY bcrypt?
- bcrypt is intentionally slow, making brute-force attacks expensive.
- It automatically handles salting (random data mixed with the password).

WHY JWT?
- JWTs are self-contained tokens. The backend can verify them without a database lookup.
- The frontend stores the JWT and sends it with every request via the Authorization header.
- We use short-lived access tokens (30 min) and long-lived refresh tokens (7 days).
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv(override=True)

# ==================================================
# CONFIGURATION
# ==================================================
# Educational Comment:
# In production, JWT_SECRET must be a strong, random string stored in environment
# variables. NEVER hardcode secrets in source code.

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev-refresh-secret-change-in-production")
JWT_ACCESS_EXPIRY_MINUTES = 30
JWT_REFRESH_EXPIRY_DAYS = 7
JWT_ALGORITHM = "HS256"


# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(plain_password: str) -> str:
    """
    Hashes a plaintext password using bcrypt.
    The result includes the salt, so we don't need to store it separately.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored bcrypt hash.
    Returns True if they match, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ==================================================
# JWT TOKEN MANAGEMENT
# ==================================================

def create_access_token(user_id: str, organization_id: str, role: str, session_id: str) -> str:
    """
    Creates a short-lived JWT access token containing the user's identity and session ID.
    This token is sent with every API request in the Authorization header.
    
    Educational Comment:
    We embed the `session_id` in the JWT so the middleware can easily query MongoDB
    to ensure the session hasn't been revoked, combining stateless JWT benefits with
    stateful revocation capabilities.
    """
    payload = {
        "sub": user_id,              # Subject — who this token belongs to
        "org": organization_id,       # Organization — multi-tenant isolation
        "role": role,                 # Role — for RBAC (but backend always re-verifies)
        "sid": session_id,            # Session ID — links to the active session in MongoDB
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_EXPIRY_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str, session_id: str) -> str:
    """
    Creates a long-lived refresh token used to obtain new access tokens
    without requiring the user to log in again.
    
    Educational Comment:
    Includes the `session_id` so we can tie this refresh token directly to the
    active session in the database.
    """
    payload = {
        "sub": user_id,
        "sid": session_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_EXPIRY_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a JWT access token.
    Returns the payload dict if valid, None if expired or tampered.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a JWT refresh token.
    Returns the payload dict if valid, None if expired or tampered.
    """
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
