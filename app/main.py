from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select
from app.models import Client, Deal
from typing import List
from app.schemas import ClientCreate, DealCreate, ClientRead, DealRead
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()

origins = [
    "http://localhost:5173",    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "I am Tiny CRM and I am alive!"}

# Create a new client
@app.post("/clients/", response_model=ClientRead)
def create_client(client_in: ClientCreate):
    with Session(engine) as session:
        client = Client(name=client_in.name, 
                        email=client_in.email,
                        phone=client_in.phone,
                        address=client_in.address
                        )
        session.add(client)
        session.commit()
        session.refresh(client)
    return client

# Get all clients
@app.get("/clients/", response_model=List[ClientRead])
def get_clients():
    with Session(engine) as session:
        return session.exec(
            select(Client).where(Client.is_active == True)
        ).all()

@app.get("/clients/by_query", response_model=List[ClientRead])
def search_clients(query: str):
    with Session(engine) as session:
        stmt = (
            select(Client)
            .where(
                Client.is_active == True,  # ← filter
                (Client.name.ilike(f"%{query}%")) | (Client.email.ilike(f"%{query}%"))
            )
        )
        return session.exec(stmt).all()



# Find client by ID
@app.get('/clients/{client_id}', response_model=ClientRead)
def get_client(client_id: int):
    with Session(engine) as session:
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
   
    
# Create a new deal
@app.post("/deals", response_model=DealRead)
def create_deal(deal_in: DealCreate):
    with Session(engine) as session:
        client = session.get(Client, deal_in.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        deal = Deal(
            client_id=deal_in.client_id,
            amount=deal_in.amount,
            status=deal_in.status,
            notes=deal_in.notes
        )
        session.add(deal)
        session.commit()
        session.refresh(deal)
        return deal

# Get a deal by ID
@app.put("/deals/{deal_id}", response_model=DealRead)
def update_deal(deal_id: int, updated_deal: DealCreate):
    with Session(engine) as session:
        deal = session.get(Deal, deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        deal.status = updated_deal.status
        deal.notes = updated_deal.notes 
        session.add(deal)
        session.commit()
        session.refresh(deal)
        return deal

@app.get("/deals/", response_model=List[DealRead])
def get_deals():
    with Session(engine) as session:
        deals = session.exec(select(Deal)).all()
        return deals
    

@app.get("/deals/filter", response_model=List[DealRead])
def filter_deals_by_status(status: str):
    with Session(engine) as session:
        deals = session.exec(select(Deal).where(Deal.status == status)).all()
        return deals


@app.delete("/clients/{client_id}", response_model=ClientRead)
def deactivate_client(client_id: int):
    with Session(engine) as session:
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404)
        client.is_active = False
        session.add(client)
        session.commit()
        session.refresh(client)
        return client
    

@app.get("/clients/inactive", response_model=List[ClientRead])
def get_inactive_clients():
    with Session(engine) as session:
        return session.exec(select(Client).where(Client.is_active == False)).all()

