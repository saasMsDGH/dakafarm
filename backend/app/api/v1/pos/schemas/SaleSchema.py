from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.api.v1.pos.schemas.CustomerSchema import CustomerResponse
from app.api.v1.pos.schemas.PaymentSchema import PaymentResponse

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class SaleItemResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal

    model_config = {"from_attributes": True}

class SaleCreate(BaseModel):
    customer_id: int
    discount: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    amount_paid: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    payment_method: Optional[str] = Field(None, description="Required if amount_paid > 0")
    items: List[SaleItemCreate] = Field(..., min_length=1)

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    sale_date: datetime
    subtotal: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    payment_status: str
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    items: List[SaleItemResponse] = []
    payments: List[PaymentResponse] = []

    model_config = {"from_attributes": True}

class SaleListResponse(BaseModel):
    items: List[SaleResponse]
    total: int
    page: int
    limit: int
    pages: int

