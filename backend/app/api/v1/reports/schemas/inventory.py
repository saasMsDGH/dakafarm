from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class CurrentStockItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    unit_of_measure: str
    current_stock: Decimal
    reorder_level: Decimal
    stock_status: str  # IN_STOCK, LOW_STOCK, OUT_OF_STOCK


class CurrentStockReport(BaseModel):
    items: List[CurrentStockItem]
    total: int
    page: int
    limit: int
    pages: int


class StockMovementItem(BaseModel):
    id: int
    movement_date: datetime
    product_name: str
    category: Optional[str] = None
    movement_type: str
    quantity: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}


class StockMovementReport(BaseModel):
    items: List[StockMovementItem]
    total: int
    page: int
    limit: int
    pages: int


class LowStockItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    current_stock: Decimal
    reorder_level: Decimal
    difference: Decimal


class InventoryValuationItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    quantity: Decimal
    cost_per_unit: Decimal
    stock_value: Decimal


class InventoryValuationReport(BaseModel):
    items: List[InventoryValuationItem]
    total_value: Decimal
