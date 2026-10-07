"""StockGuard API entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import auth, items
from app.core.config import get_settings
from app.db.database import Base, engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create local database tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    yield

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(items.router)

@app.get("/healthcheck", tags=["Operations"])
def health() -> dict[str, str]:
    """Return application health."""
    return {"status": "ok"}
