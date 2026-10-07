"""Authentication use cases."""
from fastapi import HTTPException, status
from app.services.auth_service import authenticate, create_token

def login(username: str, password: str) -> dict[str, str]:
    """Authenticate a user and issue a bearer token."""
    if not authenticate(username, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_token(username), "token_type": "bearer"}
