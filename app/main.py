"""StockGuard API entry point."""
from contextlib import asynccontextmanager
from collections.abc import Iterator
from fastapi import FastAPI
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker
from app.api.routes import auth, items
from app.core.config import get_settings
from app.db.database import Base, SessionLocal, engine, get_db
from app.services.auth_service import bootstrap_admin

settings = get_settings()


def create_app(
    db_engine: Engine = engine,
    session_factory: sessionmaker[Session] = SessionLocal,
    *,
    bootstrap: bool = True,
) -> FastAPI:
    """Build the API with an explicit database and optional admin bootstrap."""
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(bind=db_engine)
        if bootstrap:
            with session_factory() as db:
                bootstrap_admin(db, settings)
        yield

    application = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    def database_session() -> Iterator[Session]:
        with session_factory() as db:
            yield db

    application.dependency_overrides[get_db] = database_session
    application.include_router(auth.router)
    application.include_router(items.router)
    application.add_api_route("/health", health, methods=["GET"], tags=["Operations"])
    return application


def health() -> dict[str, str]:
    """Return application health."""
    return {"status": "ok"}


app = create_app()
