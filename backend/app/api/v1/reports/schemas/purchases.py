from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class PurchasesSummary(BaseModel):
    total_purchases: int
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class PurchasesDetailItem(BaseModel):
    id: int
    purchase_number: str
    purchase_date: datetime
    supplier_name: Optional[str] = None
    subtotal: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class PurchasesDetailReport(BaseModel):
    items: List[PurchasesDetailItem]
    total: int
    page: int
    limit: int
    pages: int
    summary: PurchasesSummary


class PurchasesBySupplierItem(BaseModel):
    supplier_id: int
    supplier_name: str
    num_purchases: int
    total_purchases: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class PurchasesByProductItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    quantity_purchased: Decimal
    total_cost: Decimal
    avg_unit_cost: Decimal
