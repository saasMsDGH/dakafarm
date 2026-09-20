from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class AssetRegisterItem(BaseModel):
    id: int
    asset_code: str
    name: str
    description: Optional[str] = None
    purchase_date: Optional[date] = None
    cost_price: Decimal
    quantity: int
    condition: Optional[str] = None
    depreciation_rate: Optional[Decimal] = None
    status: Optional[str] = None
    amount_paid: Decimal
    payment_status: Optional[str] = None

    model_config = {"from_attributes": True}


class AssetRegisterReport(BaseModel):
    items: List[AssetRegisterItem]
    total: int
    page: int
    limit: int
    pages: int
    total_cost: Decimal
    total_paid: Decimal
    outstanding: Decimal


class AssetsByConditionItem(BaseModel):
    condition: str
    num_assets: int
    total_cost: Decimal
