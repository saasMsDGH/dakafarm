from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Request Schemas ---

class ExpenseCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100, description="Expense category (e.g. Transport, Electricity, Salary)")
    description: Optional[str] = Field(None, description="Details of the expense")
    amount: Decimal = Field(..., gt=0, description="Expense amount")
    expense_date: Optional[datetime] = Field(None, description="Date of expense (defaults to now)")
    payment_method: str = Field(..., min_length=1, description="Cash, Mobile Money, or Bank Transfer")

class ExpenseUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    expense_date: Optional[datetime] = None
    payment_method: Optional[str] = Field(None, min_length=1)

# --- Response Schemas ---

class ExpenseResponse(BaseModel):
    id: int
    expense_number: str
    category: str
    description: Optional[str]
    amount: Decimal
    expense_date: datetime
    payment_method: str
    paid_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ExpenseListResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    page: int
    limit: int
    pages: int
