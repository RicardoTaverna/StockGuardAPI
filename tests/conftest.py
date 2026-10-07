"""Self-contained test configuration and per-test SQLite databases."""
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import Settings

# Construct settings explicitly: neither the shell nor .env supplies test credentials.
# Patch before importing modules that cache settings at import time.
test_settings = Settings(
    _env_file=None,
    app_name="StockGuard API",
    app_env="test",
    database_url="sqlite://",
    jwt_secret="stockguard-test-only-secret",
    jwt_algorithm="HS256",
    access_token_minutes=30,
    bootstrap_user="",
    bootstrap_password="",
)
with patch("app.core.config.get_settings", return_value=test_settings):
    from app.db.database import Base
    from app.main import create_app
    from app.models.user import User
    from app.services.auth_service import hash_password


@pytest.fixture(autouse=True)
def database():
    """Create schema and reviewer in a fresh shared in-memory database per test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    sessions = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    try:
        Base.metadata.create_all(bind=engine)
        with sessions() as db:
            db.add(User(username="reviewer", password_hash=hash_password("reviewer-pass")))
            db.commit()
        yield engine, sessions
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(database):
    """Exercise real startup and routes against only the test database."""
    engine, sessions = database
    application = create_app(engine, sessions, bootstrap=False)
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    """Authenticate the seeded reviewer and report login failures clearly."""
    response = client.post(
        "/auth/token", data={"username": "reviewer", "password": "reviewer-pass"},
    )
    assert response.status_code == 200, (
        f"Authentication failed for test reviewer: HTTP {response.status_code}: {response.text}"
    )
    token = response.json().get("access_token")
    assert isinstance(token, str) and token, "Authentication response has no valid access_token"
    return {"Authorization": f"Bearer {token}"}
