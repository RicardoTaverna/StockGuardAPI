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

def test_deactivate_item(client, auth_headers):
    payload = {
        "sku": "GPU-001",
        "name": "Graphics Card",
        "quantity": 4,
        "unit_price": 1999.9,
    }

    item = client.post(
        "/items",
        json=payload,
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/items/{item['id']}/deactivate",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["active"] is False
    assert response.json()["quantity"] == 4

def test_deactivate_missing_item(client, auth_headers):
    response = client.patch(
        "/items/9999/deactivate",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
