from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.api.v1.pos.schemas.PurchasePaymentSchema import PurchasePaymentResponse

class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)
    new_selling_price: Optional[Decimal] = Field(None, ge=0, description="Optionally update the product selling price")

class PurchaseItemResponse(BaseModel):
    id: int
    purchase_id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    total_amount: Decimal

    model_config = {"from_attributes": True}

class PurchaseCreate(BaseModel):
    supplier_id: int
    discount: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    amount_paid: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    payment_method: Optional[str] = Field(None, description="Required if amount_paid > 0")
    notes: Optional[str] = None
    items: List[PurchaseItemCreate] = Field(..., min_length=1)

class PurchaseResponse(BaseModel):
    id: int
    purchase_number: str
    supplier_id: int
    purchase_date: datetime
    subtotal: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    payment_status: str
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseItemResponse] = []
    payments: List[PurchasePaymentResponse] = []

    model_config = {"from_attributes": True}

class PurchaseListResponse(BaseModel):
    items: List[PurchaseResponse]
    total: int
    page: int
    limit: int
    pages: int
