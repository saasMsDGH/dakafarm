from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Request Schemas ---

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Customer name")
    business_type: Optional[str] = Field(None, max_length=100, description="Type of business (e.g. Retail, Wholesale)")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[str] = Field(None, max_length=100, description="Email address")
    address: Optional[str] = Field(None, max_length=255, description="Physical address")
    credit_limit: Optional[Decimal] = Field(Decimal('0.00'), ge=0, description="Credit limit for the customer")

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    business_type: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    credit_limit: Optional[Decimal] = Field(None, ge=0)

# --- Response Schemas ---

class CustomerResponse(BaseModel):
    id: int
    customer_code: str
    name: str
    business_type: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    credit_limit: Decimal
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CustomerListResponse(BaseModel):
    items: List[CustomerResponse]
    total: int
    page: int
    limit: int
    pages: int
