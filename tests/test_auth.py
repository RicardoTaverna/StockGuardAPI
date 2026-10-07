"""Regressions for persisted login, bootstrap and database isolation."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.core.config import Settings
from app.main import create_app
from app.models.item import Item
from app.models.user import User
from app.services.auth_service import authenticate, bootstrap_admin, hash_password


def test_reviewer_login(client, database):
    response = client.post(
        "/auth/token", data={"username": "reviewer", "password": "reviewer-pass"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    with database[1]() as db:
        user = db.scalar(select(User).where(User.username == "reviewer"))
        assert user.password_hash != "reviewer-pass"
        assert user.active
        assert user.role is None
        assert db.scalar(select(func.count()).select_from(User)) == 1


@pytest.mark.parametrize("username,password", [
    ("reviewer", "wrong-password"), ("missing", "reviewer-pass"),
])
def test_invalid_credentials(client, username, password):
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_inactive_user_cannot_login(client, database):
    with database[1]() as db:
        user = db.scalar(select(User).where(User.username == "reviewer"))
        user.active = False
        db.commit()
    assert client.post(
        "/auth/token", data={"username": "reviewer", "password": "reviewer-pass"},
    ).status_code == 401


def test_login_uses_persisted_password(client, database):
    with database[1]() as db:
        user = db.scalar(select(User).where(User.username == "reviewer"))
        user.password_hash = hash_password("changed-password")
        db.commit()
    assert client.post(
        "/auth/token", data={"username": "reviewer", "password": "reviewer-pass"},
    ).status_code == 401
    assert client.post(
        "/auth/token", data={"username": "reviewer", "password": "changed-password"},
    ).status_code == 200


def test_bootstrap_creates_admin_and_never_overwrites(database):
    config = Settings(
        _env_file=None, database_url="sqlite://", jwt_secret="test",
        bootstrap_user="admin", bootstrap_password="initial-password",
    )
    with database[1]() as db:
        bootstrap_admin(db, config)
        admin = db.scalar(select(User).where(User.username == "admin"))
        assert admin.active and admin.role == "admin"
        assert authenticate(db, "admin", "initial-password")
        original_hash = admin.password_hash
        admin.active = False
        admin.role = "custom"
        db.commit()
        bootstrap_admin(db, config.model_copy(update={"bootstrap_password": "new-password"}))
        db.refresh(admin)
        assert admin.password_hash == original_hash
        assert admin.active is False
        assert admin.role == "custom"
        assert db.scalar(select(func.count()).select_from(User)) == 2


def test_startup_bootstraps_admin_and_preserves_inventory(database, monkeypatch):
    import app.main as main

    config = main.settings.model_copy(update={
        "bootstrap_user": "admin", "bootstrap_password": "initial-password",
    })
    monkeypatch.setattr(main, "settings", config)
    with database[1]() as db:
        db.add(Item(sku="EXISTING", name="Existing item", quantity=7, unit_price=10))
        db.commit()
    for password in ("initial-password", "changed-config-password"):
        monkeypatch.setattr(main, "settings", config.model_copy(update={
            "bootstrap_password": password,
        }))
        with TestClient(create_app(*database)) as client:
            response = client.post(
                "/auth/token", data={"username": "admin", "password": "initial-password"},
            )
            assert response.status_code == 200
            headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
            listed = client.get("/items", headers=headers)
            assert listed.status_code == 200
            assert listed.json()[0]["quantity"] == 7
    with database[1]() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 2


def test_database_starts_without_inventory(database):
    with database[1]() as db:
        assert db.scalar(select(func.count()).select_from(Item)) == 0


def test_username_is_unique(database):
    with database[1]() as db:
        db.add(User(username="reviewer", password_hash=hash_password("different")))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
