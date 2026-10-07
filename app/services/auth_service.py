"""Minimal authentication service for the workshop application."""
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import get_settings

settings = get_settings()

def authenticate(username: str, password: str) -> bool:
    """Validate the single bootstrap account configured for the lab."""
    return username == settings.bootstrap_user and password == settings.bootstrap_password

def create_token(username: str) -> str:
    """Create a short-lived bearer token."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": username, "exp": expires}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
