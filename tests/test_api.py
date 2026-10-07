"""Endpoint tests for the base application."""
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_items_require_authentication(client):
    assert client.get("/items").status_code == 401

def test_create_and_list_item(client, auth_headers):
    payload = {"sku": "SSD-001", "name": "SSD 1TB", "quantity": 10, "unit_price": 399.9}
    created = client.post("/items", json=payload, headers=auth_headers)
    assert created.status_code == 201
    listed = client.get("/items", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["sku"] == "SSD-001"

def test_withdraw_stock(client, auth_headers):
    payload = {"sku": "RAM-001", "name": "Memory 16GB", "quantity": 8, "unit_price": 249.9}
    item = client.post("/items", json=payload, headers=auth_headers).json()
    response = client.post(f"/items/{item['id']}/withdraw", json={"quantity": 3, "reason": "Order 42"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

def test_reserve_stock(client, auth_headers):
    payload = {
        "sku": "SSD-RES-001",
        "name": "SSD 1TB",
        "quantity": 10,
        "unit_price": 499.9,
    }

    item = client.post(
        "/items",
        json=payload,
        headers=auth_headers,
    ).json()

    response = client.post(
        f"/items/{item['id']}/reserve",
        json={"quantity": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 10
    assert response.json()["reserved_quantity"] == 3

def test_cannot_reserve_more_than_available_stock(client, auth_headers):
    payload = {
        "sku": "SSD-RES-002",
        "name": "SSD 2TB",
        "quantity": 5,
        "unit_price": 799.9,
    }

    item = client.post(
        "/items",
        json=payload,
        headers=auth_headers,
    ).json()

    response = client.post(
        f"/items/{item['id']}/reserve",
        json={"quantity": 6},
        headers=auth_headers,
    )

    assert response.status_code == 409

def test_multiple_reservations_consider_available_stock(client, auth_headers):
    payload = {
        "sku": "SSD-RES-003",
        "name": "SSD 4TB",
        "quantity": 10,
        "unit_price": 1299.9,
    }

    item = client.post(
        "/items",
        json=payload,
        headers=auth_headers,
    ).json()

    first = client.post(
        f"/items/{item['id']}/reserve",
        json={"quantity": 7},
        headers=auth_headers,
    )

    assert first.status_code == 200
    assert first.json()["reserved_quantity"] == 7

    second = client.post(
        f"/items/{item['id']}/reserve",
        json={"quantity": 4},
        headers=auth_headers,
    )

    assert second.status_code == 409
