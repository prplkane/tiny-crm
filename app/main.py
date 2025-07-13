# app/main.py

from datetime import datetime, timezone, date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import or_
from sqlmodel import Session, create_engine, select, SQLModel

from dotenv import load_dotenv
import os

from app.models import Client, Deal, Procedure, WorkflowStatus, PaymentStatus
from app.schemas import ClientCreate, ClientRead, DealCreate, DealRead

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

# Dependency to get a DB session
def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/", summary="Health check")
def read_root():
    return {"message": "I am Tiny CRM and I am alive!"}


# ─── CLIENT ENDPOINTS -───────────────────────────────────────────────

#Create a new client
@app.post("/clients/", response_model=ClientRead, summary="Create a client")
def create_client(client_in: ClientCreate, session: Session = Depends(get_session)): # Use the dependency
    client = Client.from_orm(client_in)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

# Read all active clients
@app.get("/clients/", response_model=List[ClientRead], summary="List active clients")
def get_clients(session: Session = Depends(get_session)):
    return session.exec(
        select(Client).where(Client.is_active == True)
    ).all()


#Search for clients by name, phone or email
@app.get("/clients/search", response_model=List[ClientRead], summary="Search active clients")
def search_clients(
    q: str = Query(..., min_length=1, description="Fragment of first/last/middle name, phone or email"),
    session: Session = Depends(get_session) # Use the dependency
):
    stmt = (
        select(Client)
        .where(
            Client.is_active == True,
            or_(
                Client.first_name.ilike(f"%{q}%"),
                Client.last_name.ilike(f"%{q}%"),
                Client.middle_name.ilike(f"%{q}%"),
                Client.phone.ilike(f"%{q}%"),
                Client.email.ilike(f"%{q}%"), # You were missing email in the search
            ),
        )
    )
    results = session.exec(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail="No clients found")
    return results


# Get client by ID
@app.get("/clients/{client_id}", response_model=ClientRead, summary="Get client by ID")
def get_client(client_id: int, session: Session = Depends(get_session)): # Use the dependency
    client = session.get(Client, client_id)
    if not client or not client.is_active:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

# Delete a client
@app.delete("/clients/{client_id}", response_model=ClientRead, summary="Deactivate a client")
def deactivate_client(client_id: int, session: Session = Depends(get_session)): # Use the dependency
    client = session.get(Client, client_id)
    if not client or not client.is_active:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_active = False
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

# List all inactive clients
@app.get("/clients/inactive", response_model=List[ClientRead], summary="List inactive clients")
def get_inactive_clients(session: Session = Depends(get_session)): # Use the dependency
    return session.exec(select(Client).where(Client.is_active == False)).all()

# ─── DEAL ENDPOINTS -───────────────────────────────────────────────

@app.post("/deals", response_model=DealRead, summary="Create a new deal")
def create_deal(deal_in: DealCreate, session: Session = Depends(get_session)):
    client = session.get(Client, deal_in.client_id)
    if not client or not client.is_active:
        raise HTTPException(status_code=404, detail="Client not found")

    deal = Deal.model_validate(deal_in)

    deal.tax_amount = deal.amount_gross * deal.tax_rate
    deal.amount_net = deal.amount_gross - deal.discount + deal.tax_amount
    
    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal

# Update an existing deal
@app.put("/deals/{deal_id}", response_model=DealRead, summary="Update an existing deal")
def update_deal(deal_id: int, deal_in: DealCreate, session: Session = Depends(get_session)):
    deal = session.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal_data = deal_in.model_dump(exclude_unset=True)
    for key, value in deal_data.items():
        setattr(deal, key, value)

    deal.tax_amount = deal.amount_gross * deal.tax_rate
    deal.amount_net = deal.amount_gross - deal.discount + deal.tax_amount
    deal.updated_at = datetime.now(timezone.utc)

    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal

# Get all deals
@app.get("/deals/", response_model=List[DealRead], summary="List all deals")
def get_deals(session: Session = Depends(get_session)): # Use the dependency
    return session.exec(select(Deal)).all()

# Search deals by various criteria
@app.get("/deals/search", response_model=List[DealRead], summary="Filter deals")
def search_deals(
    status: Optional[WorkflowStatus] = None, # FIX: Query param name to match schema
    payment_status: Optional[PaymentStatus] = None,
    category: Optional[Procedure] = None,
    client_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    session: Session = Depends(get_session)
):
    stmt = select(Deal)
    if status:
        # FIX: Use Deal.status to match the model rename
        stmt = stmt.where(Deal.status == status)
    if payment_status:
        stmt = stmt.where(Deal.payment_status == payment_status)
    if category:
        stmt = stmt.where(Deal.category == category)
    if client_id:
        stmt = stmt.where(Deal.client_id == client_id)
    if date_from:
        stmt = stmt.where(Deal.invoice_date >= date_from)
    if date_to:
        stmt = stmt.where(Deal.invoice_date <= date_to)

    return session.exec(stmt).all()