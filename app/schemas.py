# app/schemas.py

from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime, date
from typing import Optional, List

from app.models import (
    Procedure,
    WorkflowStatus,
    PaymentStatus,
)


# ─── CLIENT SCHEMAS 

class ClientCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientRead(BaseModel):
    id:          int
    first_name:  str
    middle_name: Optional[str]
    last_name:   str
    email:       Optional[EmailStr]
    phone:       Optional[str]
    address:     Optional[str]
    is_active:   bool
    created_at:  datetime

    model_config = ConfigDict(from_attributes=True)


# ─── DEAL SCHEMAS 

class DealCreate(BaseModel):
    client_id:      int
    category:       Procedure

    # Financial inputs
    amount_gross:   float
    discount:       Optional[float]       = 0.0
    tax_rate:       Optional[float]       = 0.0    # fraction, e.g. 0.12
    payment_method: Optional[str]         = None
    invoice_number: Optional[str]         = None
    due_date:       Optional[date]        = None

    # Workflow & payment state (you can override on create if you like)
    status:         WorkflowStatus        = WorkflowStatus.open
    payment_status: PaymentStatus         = PaymentStatus.unpaid

    notes:          Optional[str]         = None


class DealRead(BaseModel):
    id:              int
    client_id:       int
    category:        Procedure

    # Workflow & payment
    status:          WorkflowStatus
    payment_status:  PaymentStatus

    # Financial breakdown
    amount_gross:    float
    discount:        float
    tax_rate:        float
    tax_amount:      float
    amount_net:      float
    currency:        str

    paid_amount:     Optional[float]
    payment_method:  Optional[str]

    # Invoicing dates
    invoice_number:  Optional[str]
    invoice_date:    datetime
    due_date:        Optional[date]
    paid_date:       Optional[datetime]

    # Notes & audit
    notes:           Optional[str]
    created_at:      datetime
    updated_at:      Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
