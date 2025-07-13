from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


#Client models
class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    

class ClientRead(BaseModel):
    id:int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    created_at: datetime
    is_active: bool = True

    
    model_config = ConfigDict(from_attributes=True)

#Deals model
class DealCreate(BaseModel):
    client_id: int
    amount: float
    status: Optional[str] = 'open'
    notes: Optional[str] = None

class DealRead(BaseModel):
    id: int
    client_id: int
    amount: float
    status: str
    notes: Optional[str] = None
    created_at: datetime    

    model_config = ConfigDict(from_attributes=True)