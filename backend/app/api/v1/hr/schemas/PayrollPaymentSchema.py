from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class PayrollPaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount paid")
    payment_method: str = Field(..., max_length=50, description="e.g. CASH, BANK TRANSFER, MOBILE MONEY")
    account_id: int = Field(..., description="Financial account ID")

class PayrollPaymentResponse(BaseModel):
    id: int
    payroll_id: int
    account_id: int
    payment_reference: str
    amount: Decimal
    payment_method: str
    payment_date: datetime
    paid_by: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
