from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# --- Request Schemas ---

class AssetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    purchase_date: Optional[date] = None
    cost_price: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    quantity: Optional[int] = Field(1, ge=1)
    condition: Optional[str] = Field("Good", max_length=50)
    depreciation_rate: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    status: Optional[str] = Field("Active", max_length=50)

    amount_paid: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    account_id: Optional[int] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    purchase_date: Optional[date] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=1)
    condition: Optional[str] = Field(None, max_length=50)
    depreciation_rate: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    payment_status: Optional[str] = Field(None, max_length=50)

class AssetDistributionCreate(BaseModel):
    location: str = Field(..., min_length=1, max_length=150)
    quantity: int = Field(..., ge=1)
    assigned_date: Optional[date] = None
    notes: Optional[str] = None

# --- Response Schemas ---

class AssetDistributionResponse(BaseModel):
    id: int
    asset_id: int
    location: str
    quantity: int
    assigned_date: Optional[date]
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    
    model_config = {"from_attributes": True}

class AssetResponse(BaseModel):
    id: int
    asset_code: str
    name: str
    description: Optional[str]
    purchase_date: Optional[date]
    cost_price: Decimal
    quantity: int
    condition: str
    depreciation_rate: Decimal
    status: str
    amount_paid: Decimal
    payment_status: str
    
    distributions: List[AssetDistributionResponse] = []

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
