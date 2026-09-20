from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class CashBookEntry(BaseModel):
    id: int
    transaction_date: datetime
    reference_number: Optional[str] = None
    description: Optional[str] = None
    transaction_type: str
    direction: str
    amount: Decimal
    money_in: Optional[Decimal] = None
    money_out: Optional[Decimal] = None
    running_balance: Decimal

    model_config = {"from_attributes": True}


class CashBookReport(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    opening_balance: Decimal
    total_in: Decimal
    total_out: Decimal
    closing_balance: Decimal
    items: List[CashBookEntry]
    total: int
    page: int
    limit: int
    pages: int


class FinancialTransactionReportItem(BaseModel):
    id: int
    transaction_date: datetime
    reference_number: Optional[str] = None
    description: Optional[str] = None
    transaction_type: str
    account_id: int
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    direction: str
    amount: Decimal
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialTransactionReport(BaseModel):
    items: List[FinancialTransactionReportItem]
    total: int
    page: int
    limit: int
    pages: int
    total_in: Decimal
    total_out: Decimal
    net: Decimal


class AccountSummaryItem(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    opening_balance: Decimal
    total_in: Decimal
    total_out: Decimal
    closing_balance: Decimal


class AccountSummaryReport(BaseModel):
    items: List[AccountSummaryItem]
    grand_total_in: Decimal
    grand_total_out: Decimal
    grand_net: Decimal


class DailyFinancialSummary(BaseModel):
    date: str
    total_in: Decimal
    total_out: Decimal
    net: Decimal
    cash_in: Decimal
    cash_out: Decimal
    bank_in: Decimal
    bank_out: Decimal
    mobile_in: Decimal
    mobile_out: Decimal
