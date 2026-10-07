"""Database-backed authentication and initial account provisioning."""
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import Settings, get_settings
from app.models.user import User

settings = get_settings()
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password with a randomly generated salt."""
    return password_context.hash(password)


def authenticate(db: Session, username: str, password: str) -> bool:
    """Validate the password of an active persisted account."""
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.active:
        return False
    return password_context.verify(password, user.password_hash)


def bootstrap_admin(db: Session, config: Settings) -> None:
    """Create the configured admin without modifying an existing account."""
    user = db.scalar(select(User).where(User.username == config.bootstrap_user))
    if user is not None:
        return
    db.add(User(
        username=config.bootstrap_user,
        password_hash=hash_password(config.bootstrap_password),
        active=True,
        role="admin",
    ))
    db.commit()


def create_token(username: str) -> str:
    """Create a short-lived bearer token."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": username, "exp": expires}, settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
