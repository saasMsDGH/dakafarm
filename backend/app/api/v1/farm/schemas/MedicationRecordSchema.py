"""
MedicationRecord schemas — request validation and response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ── Request schemas ────────────────────────────────────────────────────────────

class MedicationRecordCreate(BaseModel):
    """Body for POST /medication-records."""
    flock_id: int = Field(..., description="ID of the flock being medicated")
    product_id: Optional[int] = Field(None, description="Loose reference to the medication product")
    record_date: date = Field(..., description="Date the medication was given")
    
    disease_suspected: Optional[str] = Field(None, max_length=255, description="Suspected disease")
    
    quantity_used: Decimal = Field(..., gt=0, description="Amount of medication used")
    cost_per_unit: Optional[Decimal] = Field(None, ge=0, description="Cost per unit of medication")
    
    # Notice: total_cost is omitted. The backend fully automates its calculation.
    
    withdrawal_period_days: Optional[int] = Field(0, ge=0, description="Safe consumption gap in days")


class MedicationRecordUpdate(BaseModel):
    """Body for PUT /medication-records/{id}."""
    flock_id: Optional[int] = None
    product_id: Optional[int] = None
    record_date: Optional[date] = None
    disease_suspected: Optional[str] = Field(None, max_length=255)
    quantity_used: Optional[Decimal] = Field(None, gt=0)
    cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    withdrawal_period_days: Optional[int] = Field(None, ge=0)


# ── Response schemas ───────────────────────────────────────────────────────────

class MedicationRecordResponse(BaseModel):
    """Single medication record response."""
    id: int
    flock_id: int
    product_id: Optional[int] = None
    record_date: date
    disease_suspected: Optional[str] = None
    
    quantity_used: Decimal
    cost_per_unit: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    withdrawal_period_days: int
    
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MedicationRecordListResponse(BaseModel):
    """Paginated list of medication records."""
    items: List[MedicationRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
