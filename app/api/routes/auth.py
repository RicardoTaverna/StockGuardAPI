"""Authentication routes."""
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.controllers.auth_controller import login
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token")
def token(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db),
) -> dict[str, str]:
    """Issue an access token for valid credentials."""
    return login(db, username, password)
