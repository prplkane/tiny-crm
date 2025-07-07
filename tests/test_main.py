import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_crud_and_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Root endpoint
        resp = await ac.get("/")
        assert resp.status_code == 200
        assert resp.json()["message"].startswith("I am Tiny CRM")

        # Create a client
        client_data = {"name": "Alice", "email": "alice@example.com"}
        resp = await ac.post("/clients/", json=client_data)
        assert resp.status_code == 200
        client = resp.json()
        client_id = client["id"]

        # Get all clients
        resp = await ac.get("/clients/")
        assert resp.status_code == 200
        assert any(c["id"] == client_id for c in resp.json())

        # Get client by ID
        resp = await ac.get(f"/clients/{client_id}")
        assert resp.status_code == 200

        # Search client
        resp = await ac.get("/clients/by_query", params={"query": "Alice"})
        assert resp.status_code == 200
        assert any(c["id"] == client_id for c in resp.json())

        # Create a deal
        deal_data = {"client_id": client_id, "amount": 500.0, "status": "open"}
        resp = await ac.post("/deals", json=deal_data)
        assert resp.status_code == 200
        deal = resp.json()
        deal_id = deal["id"]

        # Update deal
        update_data = {"client_id": client_id, "amount": 750.0, "status": "won"}
        resp = await ac.put(f"/deals/{deal_id}", json=update_data)
        assert resp.status_code == 200
        assert resp.json()["status"] == "won"

        # Get all deals
        resp = await ac.get("/deals/")
        assert resp.status_code == 200
        assert any(d["id"] == deal_id for d in resp.json())

        # Filter deals by status
        resp = await ac.get("/deals/filter", params={"status": "won"})
        assert resp.status_code == 200
        assert any(d["id"] == deal_id for d in resp.json())

        # Error: Get non-existent client
        resp = await ac.get("/clients/99999")
        assert resp.status_code == 404

        # Error: Create deal for non-existent client
        resp = await ac.post("/deals", json={"client_id": 99999, "amount": 100, "status": "open"})
        assert resp.status_code == 404

        # Error: Update non-existent deal
        resp = await ac.put("/deals/99999", json={"client_id": client_id, "amount": 100, "status": "lost"})
        assert resp.status_code == 404
