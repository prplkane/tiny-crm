from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

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
    discount: float | None = Field(default=0.0, nullable=True)
    
    status: str = Field(default='open', index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client: Client | None = Relationship(back_populates="deals")
    notes: str | None = Field(default=None, nullable=True) 