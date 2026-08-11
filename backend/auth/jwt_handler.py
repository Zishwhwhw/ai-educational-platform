# ==========================================
# File: auth/jwt_handler.py
# Description: JWT token creation and verification
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from datetime import datetime, timedelta
from typing import Optional
import hashlib
import json
import base64
import hmac
import os

SECRET_KEY = os.getenv("SECRET_KEY", "ai-code-platform-secret-key-2026-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def _base64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    data += "=" * padding
    return base64.urlsafe_b64decode(data)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.timestamp()})
    
    header = _base64url_encode(json.dumps({"alg": ALGORITHM, "typ": "JWT"}).encode())
    payload = _base64url_encode(json.dumps(to_encode, default=str).encode())
    signature = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    sig_encoded = _base64url_encode(signature)
    
    return f"{header}.{payload}.{sig_encoded}"

def verify_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        expected_sig = _base64url_encode(
            hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected_sig):
            return None
        decoded = json.loads(_base64url_decode(payload))
        if datetime.utcnow().timestamp() > decoded.get("exp", 0):
            return None
        return decoded
    except Exception:
        return None
