# app/models.py

from datetime import datetime, timezone, date
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Procedure(str, Enum):
    cleaning    = 'cleaning'
    filling     = 'filling'
    extraction  = 'extraction'
    root_canal  = 'root_canal'
    crown       = 'crown'


class WorkflowStatus(str, Enum):
    open         = "open"
    in_progress  = "in_progress"
    invoiced     = "invoiced"
    closed       = "closed"
    cancelled    = "cancelled"


class PaymentStatus(str, Enum):
    unpaid   = 'unpaid'
    partial  = 'partial'
    paid     = 'paid'
    overdue  = 'overdue'
    refunded = 'refunded'


class Client(SQLModel, table=True):
    id:         Optional[int]  = Field(default=None, primary_key=True)
    first_name: str
    last_name:  str
    middle_name: Optional[str] = Field(default=None, nullable=True)

    phone:   Optional[str]     = Field(default=None, nullable=True)
    email:   Optional[str]     = Field(default=None, nullable=True)
    address: Optional[str]     = Field(default=None, nullable=True)

    is_active:  bool           = Field(default=True, index=True)
    created_at: datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))

    deals: List["Deal"]        = Relationship(back_populates="client")


class Deal(SQLModel, table=True):
    id:             Optional[int]    = Field(default=None, primary_key=True)
    client_id:      int             = Field(foreign_key="client.id", index=True)

    # PROCEDURE & CLINICAL WORKFLOW
    category:       Procedure
    status: WorkflowStatus = Field(default=WorkflowStatus.open, index=True)

    # FINANCIALS
    amount_gross:   float
    discount:       float        = Field(default=0.0)
    tax_rate:       float        = Field(default=0.0)  
    tax_amount:     float        = Field(default=0.0)  
    amount_net:     float        = Field(default=0.0)  # computed = amount_gross - discount + tax_amount
    currency:       str          = Field(default='KGS')

    invoice_number: Optional[str]      = Field(default=None, nullable=True)
    invoice_date:   datetime          = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date:       Optional[date]    = Field(default=None, nullable=True)

    # PAYMENT TRACKING
    payment_status: PaymentStatus     = Field(default=PaymentStatus.unpaid, index=True)
    paid_amount:    Optional[float]   = Field(default=None, nullable=True)
    paid_date:      Optional[datetime]= Field(default=None, nullable=True)
    payment_method: Optional[str]     = Field(default=None, nullable=True)

    # NOTES & AUDIT
    notes:          Optional[str]     = Field(default=None, nullable=True)
    created_at:     datetime          = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at:     Optional[datetime]= Field(default=None, nullable=True)

    client: Optional[Client] = Relationship(back_populates="deals")
