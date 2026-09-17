from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# --- Request Schemas ---

class AssetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    serial_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[date] = None
    cost_price: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    location: Optional[str] = Field(None, max_length=150)
    condition: Optional[str] = Field("Good", max_length=50)
    depreciation_rate: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    status: Optional[str] = Field("Active", max_length=50)

class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    serial_number: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[date] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=150)
    condition: Optional[str] = Field(None, max_length=50)
    depreciation_rate: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)

# --- Response Schemas ---

class AssetResponse(BaseModel):
    id: int
    asset_code: str
    name: str
    description: Optional[str]
    serial_number: Optional[str]
    purchase_date: Optional[date]
    cost_price: Decimal
    location: Optional[str]
    condition: str
    depreciation_rate: Decimal
    status: str
    
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class AssetListResponse(BaseModel):
    items: List[AssetResponse]
    total: int
    page: int
    limit: int
    pages: int
