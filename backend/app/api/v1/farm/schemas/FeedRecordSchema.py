"""
FeedRecord schemas — request validation and response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ── Request schemas ────────────────────────────────────────────────────────────

class FeedRecordCreate(BaseModel):
    """Body for POST /feed-records."""
    flock_id: int = Field(..., description="ID of the flock being fed")
    product_id: Optional[int] = Field(None, description="Loose reference to the feed product")
    record_date: date = Field(..., description="Date the feed was given")
    

    quantity_used: Decimal = Field(..., gt=0, description="Amount of feed used")

    
    cost_per_unit: Optional[Decimal] = Field(None, ge=0, description="Cost per unit of feed")
    # total_cost is auto-calculated if omitted, but can be explicitly provided



class FeedRecordUpdate(BaseModel):
    """Body for PUT /feed-records/{id}."""
    flock_id: Optional[int] = None
    product_id: Optional[int] = None
    record_date: Optional[date] = None
    
    quantity_used: Optional[Decimal] = Field(None, gt=0)

    cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)


# ── Response schemas ───────────────────────────────────────────────────────────

class FeedRecordResponse(BaseModel):
    """Single feed record response."""
    id: int
    flock_id: int
    product_id: Optional[int] = None
    record_date: date
    opening_quantity: Optional[Decimal] = None
    quantity_used: Decimal
    closing_quantity: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    recorded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FeedRecordListResponse(BaseModel):
    """Paginated list of feed records."""
    items: List[FeedRecordResponse]
    total: int
    page: int
    limit: int
    pages: int
