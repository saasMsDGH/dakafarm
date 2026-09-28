from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Request Schemas ---

class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Supplier name")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person at supplier")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[str] = Field(None, max_length=100, description="Email address")
    address: Optional[str] = Field(None, max_length=255, description="Physical address")

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)

# --- Response Schemas ---

class SupplierResponse(BaseModel):
    id: int
    supplier_code: str
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SupplierListResponse(BaseModel):
    items: List[SupplierResponse]
    total: int
    page: int
    limit: int
    pages: int
