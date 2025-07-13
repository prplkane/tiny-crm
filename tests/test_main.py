# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import app, get_session # Import get_session
from app.models import Client, Deal, Procedure, PaymentStatus

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False) # Turn off echo for cleaner test output

# This fixture will be used by each test to get a clean database
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

# This fixture provides the TestClient but overrides the get_session dependency
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# -- Tests for Client Endpoints --

def test_create_client(client: TestClient, session: Session):
    response = client.post(
        "/clients/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "address": "123 Main St",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "john.doe@example.com"
    assert "id" in data

    # Verification is now possible because the app and test use the same session
    db_client = session.get(Client, data["id"])
    assert db_client is not None
    assert db_client.first_name == "John"


def test_get_clients(client: TestClient, session: Session):
    client1 = Client(first_name="Jane", last_name="Doe", email="jane.doe@example.com", is_active=True)
    client2 = Client(first_name="Jim", last_name="Beam", email="jim.beam@example.com", is_active=False)
    session.add(client1)
    session.add(client2)
    session.commit()

    response = client.get("/clients/")
    assert response.status_code == 200
    data = response.json()
    # Now this will pass because the db is clean for this test
    assert len(data) == 1
    assert data[0]["email"] == "jane.doe@example.com"


def test_search_clients(client: TestClient, session: Session):
    client_data = Client(first_name="Search", last_name="Me", email="search.me@example.com", phone="9876543210")
    session.add(client_data)
    session.commit()

    response = client.get("/clients/search?q=Sear")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Search with no results
    response = client.get("/clients/search?q=nonexistent")
    assert response.status_code == 404


def test_deactivate_client(client: TestClient, session: Session):
    client_to_deactivate = Client(first_name="Active", last_name="Client", email="active.client@example.com")
    session.add(client_to_deactivate)
    session.commit()
    session.refresh(client_to_deactivate)

    response = client.delete(f"/clients/{client_to_deactivate.id}")
    assert response.status_code == 200
    assert not response.json()["is_active"]

    # Verify the client is now inactive
    db_client = session.get(Client, client_to_deactivate.id)
    assert not db_client.is_active


def test_create_deal(client: TestClient, session: Session):
    deal_client = Client(first_name="Deal", last_name="Maker", email="deal.maker@example.com")
    session.add(deal_client)
    session.commit()
    session.refresh(deal_client)

    response = client.post(
        "/deals",
        json={
            "client_id": deal_client.id,
            "category": Procedure.cleaning.value,
            "amount_gross": 100.0,
            "discount": 10.0,
            "tax_rate": 0.15,
            "invoice_number": "INV-001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == deal_client.id
    assert data["amount_net"] == 105.0 # 100.0 - 10.0 + (100.0 * 0.15)


def test_update_deal(client: TestClient, session: Session):
    test_client = Client(first_name="Update", last_name="Client", email="update.client@example.com")
    session.add(test_client)
    session.commit()

    test_deal = Deal(client_id=test_client.id, category=Procedure.filling, amount_gross=200.0, discount=0, tax_rate=0.1, tax_amount=20.0, amount_net=220.0, invoice_number="INV-002")
    session.add(test_deal)
    session.commit()
    session.refresh(test_deal)

    response = client.put(
        f"/deals/{test_deal.id}",
        json={
            "client_id": test_client.id,
            "category": Procedure.crown.value,
            "amount_gross": 250.0,
            "discount": 25.0,
            "tax_rate": 0.1,
            "invoice_number": "INV-002-MOD",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == Procedure.crown.value
    assert data["amount_net"] == 250.0 # 250.0 - 25.0 + (250.0 * 0.1)


def test_search_deals(client: TestClient, session: Session):
    client1 = Client(first_name="Filter", last_name="One", email="filter.one@example.com")
    client2 = Client(first_name="Filter", last_name="Two", email="filter.two@example.com")
    session.add_all([client1, client2])
    session.commit()

    deal1 = Deal(client_id=client1.id, category=Procedure.cleaning, payment_status=PaymentStatus.paid, amount_gross=50, discount=0, tax_rate=0, tax_amount=0, amount_net=50)
    deal2 = Deal(client_id=client2.id, category=Procedure.extraction, payment_status=PaymentStatus.unpaid, amount_gross=150, discount=0, tax_rate=0, tax_amount=0, amount_net=150)
    session.add_all([deal1, deal2])
    session.commit()

    response = client.get(f"/deals/search?category={Procedure.cleaning.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == Procedure.cleaning.value