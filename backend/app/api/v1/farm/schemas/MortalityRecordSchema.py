"""
MortalityRecord schemas — request validation and response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ── Request schemas ────────────────────────────────────────────────────────────

class MortalityRecordCreate(BaseModel):
    """Body for POST /mortality-records."""
    flock_id: int = Field(..., description="ID of the flock")
    record_date: date = Field(..., description="Date of the mortality event")
    quantity: int = Field(..., gt=0, description="Number of dead birds")
    cause: Optional[str] = Field(None, description="Cause of mortality if known", max_length=255)


class MortalityRecordUpdate(BaseModel):
    """Body for PUT /mortality-records/{id}."""
    flock_id: Optional[int] = None
    record_date: Optional[date] = None
    quantity: Optional[int] = Field(None, gt=0)
    cause: Optional[str] = Field(None, max_length=255)


# ── Response schemas ───────────────────────────────────────────────────────────

class MortalityRecordResponse(BaseModel):
    """Single mortality record response."""
    id: int
    flock_id: int
    record_date: date
    quantity: int
    cause: Optional[str] = None
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MortalityRecordListResponse(BaseModel):
    """Paginated list of mortality records."""
    items: List[MortalityRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
