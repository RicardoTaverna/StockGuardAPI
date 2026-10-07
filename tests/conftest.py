"""Shared test fixtures."""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_stockguard.db")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("BOOTSTRAP_USER", "reviewer")
os.environ.setdefault("BOOTSTRAP_PASSWORD", "reviewer-pass")

import pytest
from fastapi.testclient import TestClient
from app.db.database import Base, engine
from app.main import app

@pytest.fixture(autouse=True)
def reset_database():
    """Recreate database tables for every test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def client():
    """Return a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers(client):
    """Authenticate and return bearer headers."""
    response = client.post("/auth/token", data={"username": "reviewer", "password": "reviewer-pass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
