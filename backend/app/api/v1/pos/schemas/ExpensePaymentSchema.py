from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ExpensePaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)
    account_id: int = Field(..., description="Financial Account ID where the money is coming from")

class ExpensePaymentResponse(BaseModel):
    id: int
    expense_id: int
    account_id: int
    payment_reference: str
    amount: Decimal
    payment_method: str
    payment_date: datetime
    paid_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ExpensePaymentListResponse(BaseModel):
    items: List[ExpensePaymentResponse]
    total: int
    page: int
    limit: int
    pages: int
