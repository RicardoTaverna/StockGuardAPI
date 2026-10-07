"""Authentication routes."""
from fastapi import APIRouter, Form
from app.controllers.auth_controller import login
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token")
def token(username: str = Form(...), password: str = Form(...)) -> dict[str, str]:
    """Issue an access token for valid credentials."""
    return login(username, password)
