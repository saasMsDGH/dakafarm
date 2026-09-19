from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PurchasePaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)
    account_id: int = Field(..., description="Financial account from which payment is made")

class PurchasePaymentResponse(BaseModel):
    id: int
    purchase_id: int
    payment_reference: str
    amount: Decimal
    payment_method: str
    payment_date: datetime
    paid_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
