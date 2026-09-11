"""
VaccinationRecord schemas — request validation and response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ── Request schemas ────────────────────────────────────────────────────────────

class VaccinationRecordCreate(BaseModel):
    """Body for POST /vaccination-records."""
    flock_id: int = Field(..., description="ID of the flock being vaccinated")
    product_id: Optional[int] = Field(None, description="Loose reference to the vaccine product")
    record_date: date = Field(..., description="Date the vaccine was administered")
    
    disease_targeted: Optional[str] = Field(None, max_length=255, description="Target disease")
    administration_method: Optional[str] = Field(None, max_length=50, description="E.g., Water, spray, injection")
    
    quantity_used: Decimal = Field(..., gt=0, description="Amount of vaccine used")
    cost_per_unit: Optional[Decimal] = Field(None, ge=0, description="Cost per unit of vaccine")
    
    # Notice: total_cost is omitted. The backend fully automates its calculation.
    
    next_due_date: Optional[date] = Field(None, description="Date when the next dose is required")


class VaccinationRecordUpdate(BaseModel):
    """Body for PUT /vaccination-records/{id}."""
    flock_id: Optional[int] = None
    product_id: Optional[int] = None
    record_date: Optional[date] = None
    disease_targeted: Optional[str] = Field(None, max_length=255)
    administration_method: Optional[str] = Field(None, max_length=50)
    quantity_used: Optional[Decimal] = Field(None, gt=0)
    cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    next_due_date: Optional[date] = None


# ── Response schemas ───────────────────────────────────────────────────────────

class VaccinationRecordResponse(BaseModel):
    """Single vaccination record response."""
    id: int
    flock_id: int
    product_id: Optional[int] = None
    record_date: date
    disease_targeted: Optional[str] = None
    administration_method: Optional[str] = None
    
    quantity_used: Decimal
    cost_per_unit: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    next_due_date: Optional[date] = None
    
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class VaccinationRecordListResponse(BaseModel):
    """Paginated list of vaccination records."""
    items: List[VaccinationRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
