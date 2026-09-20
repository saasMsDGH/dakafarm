from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class ExpensesSummary(BaseModel):
    total_expenses: int
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class ExpensesDetailItem(BaseModel):
    id: int
    expense_number: str
    expense_date: date
    category: str
    description: Optional[str] = None
    amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_status: str
    payment_method: Optional[str] = None
    paid_by: Optional[int] = None

    model_config = {"from_attributes": True}


class ExpensesDetailReport(BaseModel):
    items: List[ExpensesDetailItem]
    total: int
    page: int
    limit: int
    pages: int
    summary: ExpensesSummary


class ExpensesByCategoryItem(BaseModel):
    category: str
    num_transactions: int
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    percentage: Decimal
