from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime, date
from typing import Optional
from app.models import Procedure, PaymentStatus


#Client models
class ClientCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    

class ClientRead(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

#Deals model
class DealCreate(BaseModel):
    client_id: int
    category: Procedure
    amount_gross: float
    discount: Optional[float] = 0.0
    tax_rate: Optional[float] = 0.0

    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[date] = None
    payment_method: Optional[str] = None

    notes: Optional[str] = None


class DealRead(BaseModel):
    id: int
    client_id: int
    category: Procedure

    amount_gross: float
    discount: float
    tax_rate: float
    tax_amount: float
    amount_net: float
    currency: str

    invoice_number: Optional[str]
    invoice_date: datetime
    due_date: Optional[date]
    paid_date: Optional[datetime]
    payment_status: PaymentStatus
    paid_amount: Optional[float]
    payment_method: Optional[str]

    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)