"""
ProductionRecord schemas — request validation and response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ── Request schemas ────────────────────────────────────────────────────────────

class ProductionRecordCreate(BaseModel):
    """Body for POST /production-records."""
    flock_id: int = Field(..., description="ID of the flock")
    record_date: date = Field(..., description="Date of the production record")
    
    total_birds: int = Field(..., ge=0, description="Total number of birds in the flock today")
    total_eggs: int = Field(..., ge=0, description="Total number of eggs collected")
    damaged_eggs: int = Field(0, ge=0, description="Number of broken/damaged eggs")
    
    # Notice: good_eggs and laying_percentage are intentionally omitted. 
    # The backend fully automates their calculation to reduce user error.


class ProductionRecordUpdate(BaseModel):
    """Body for PUT /production-records/{id}."""
    flock_id: Optional[int] = None
    record_date: Optional[date] = None
    total_birds: Optional[int] = Field(None, ge=0)
    total_eggs: Optional[int] = Field(None, ge=0)
    damaged_eggs: Optional[int] = Field(None, ge=0)


# ── Response schemas ───────────────────────────────────────────────────────────

class ProductionRecordResponse(BaseModel):
    """Single production record response."""
    id: int
    flock_id: int
    record_date: date
    
    total_birds: int
    total_eggs: int
    damaged_eggs: int
    good_eggs: int
    laying_percentage: Decimal
    
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductionRecordListResponse(BaseModel):
    """Paginated list of production records."""
    items: List[ProductionRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
