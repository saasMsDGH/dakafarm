"""
House schemas — request validation and response contracts for the House resource.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Request schemas ────────────────────────────────────────────────────────────

class HouseCreate(BaseModel):
    """Body for POST /houses — create a new house."""

    name: str = Field(..., min_length=1, max_length=100, description="Unique house name")
    location: Optional[str] = Field(None, max_length=255, description="Physical location")
    capacity: Optional[int] = Field(None, ge=1, description="Maximum bird capacity")
    description: Optional[str] = Field(None, description="Additional notes")


class HouseUpdate(BaseModel):
    """Body for PUT /houses/{id} — all fields optional for partial updates."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    capacity: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None


# ── Response schemas ───────────────────────────────────────────────────────────

class HouseResponse(BaseModel):
    """Single house response."""

    id: int
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HouseListResponse(BaseModel):
    """Paginated list of houses."""

    items: List[HouseResponse]
    total: int
    page: int
    limit: int
    pages: int
