"""FastAPI authentication dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Return the authenticated username from a bearer token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username = payload.get("sub")
        if not username:
            raise ValueError("missing subject")
        return str(username)
    except (JWTError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
