from datetime import datetime, timezone, date
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional

class PaymentStatus(str, Enum):
    unpaid = 'unpaid'
    partial = 'partial'
    paid = 'paid'
    overdue = 'overdue'
    refunded = 'refunded'

class Procedure(str, Enum):
    cleaning = 'cleaning'
    filling = 'filling'
    extraction = 'extraction'
    root_canal = 'root_canal'
    crown = 'crown'


class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    middle_name: str | None = Field(default=None, nullable=True)
    phone: str
    email: str | None = Field(default=None, nullable=True)
    address: str | None = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, index=True)   # ← NEW
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    deals: list["Deal"] = Relationship(back_populates="client")



class Deal(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    client_id: int= Field(foreign_key="client.id")
    amount: float

    category: Procedure

    amount_gross: float
    discount: float = Field(default=0.0, nullable=True)
    tax_rate: float = Field(default=0.0, nullable=True)
    tax_amount: float = Field(default=0.0, nullable=True)
    amount_net: float 
    
    currency: str = Field(default='KGS')

    invoice_number: Optional[str] = Field(default=None, nullable=True)
    invoice_date:    datetime      = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date:        Optional[date]    = Field(default=None, nullable=True)
    paid_date:       Optional[datetime]= Field(default=None, nullable=True)

    payment_status:  PaymentStatus  = Field(default=PaymentStatus.unpaid)
    paid_amount:     Optional[float]  = Field(default=None, nullable=True)
    payment_method:  Optional[str]    = Field(default=None, nullable=True)

    status:  str   = Field(default="open", index=True) # THIS IS THE ONE THAT WAS VARCHAR AND CHANGED TO ENUM
    notes:   Optional[str] = Field(default=None, nullable=True)

    created_at: datetime            = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    client: Optional[Client] = Relationship(back_populates="deals")