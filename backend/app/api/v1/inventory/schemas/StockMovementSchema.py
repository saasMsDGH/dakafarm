from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class StockMovementCreate(BaseModel):
    product_id: int = Field(..., description="ID of the product")
    movement_type: str = Field(..., description="IN, OUT, or ADJUSTMENT")
    quantity: Decimal = Field(..., description="Quantity of movement")
    reference_type: Optional[str] = Field(None, description="e.g., Purchase, Sale, FeedRecord")
    reference_id: Optional[int] = Field(None, description="ID in the referenced table")
    movement_date: Optional[datetime] = Field(None, description="Date of movement")

    @model_validator(mode='after')
    def validate_quantity(self):
        if self.movement_type in ['IN', 'OUT'] and self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0 for IN or OUT movements.")
        if self.movement_type not in ['IN', 'OUT', 'ADJUSTMENT']:
            raise ValueError("movement_type must be IN, OUT, or ADJUSTMENT")
        return self

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: Decimal
    reference_type: Optional[str]
    reference_id: Optional[int]
    movement_date: datetime
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class StockMovementListResponse(BaseModel):
    items: List[StockMovementResponse]
    total: int
    page: int
    limit: int
    pages: int
