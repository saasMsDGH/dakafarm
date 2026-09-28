from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)
    account_id: int = Field(..., description="Financial account to receive the payment")

class PaymentResponse(BaseModel):
    id: int
    sale_id: int
    receipt_number: str
    amount: Decimal
    payment_method: str
    payment_date: datetime
    received_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    page: int
    limit: int
    pages: int
