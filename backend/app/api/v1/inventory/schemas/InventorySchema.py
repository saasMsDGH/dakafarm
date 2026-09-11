from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class InventoryResponse(BaseModel):
    product_id: int
    product_name: str
    unit_of_measure: str
    quantity: Decimal
    reorder_level: Decimal
    status: str
    updated_at: Optional[datetime]

class InventoryListResponse(BaseModel):
    items: List[InventoryResponse]
    total: int
    page: int
    limit: int
    pages: int
