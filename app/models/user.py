"""Persisted authentication account."""
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class User(Base):
    """An account with an optional role reserved for future authorization."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str | None] = mapped_column(String(40), nullable=True, default=None)
