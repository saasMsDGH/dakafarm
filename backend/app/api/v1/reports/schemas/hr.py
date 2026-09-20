from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class EmployeeReportItem(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    employment_date: Optional[date] = None
    status: Optional[bool] = None

    model_config = {"from_attributes": True}


class EmployeeReport(BaseModel):
    items: List[EmployeeReportItem]
    total: int
    page: int
    limit: int
    pages: int


class PayrollSummaryByPeriod(BaseModel):
    pay_period: str
    num_employees: int
    total_basic: Decimal
    total_allowances: Decimal
    total_deductions: Decimal
    total_net: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class PayrollSummaryReport(BaseModel):
    items: List[PayrollSummaryByPeriod]
    grand_total_net: Decimal
    grand_amount_paid: Decimal
    grand_outstanding: Decimal


class PayrollDetailItem(BaseModel):
    id: int
    employee_name: str
    employee_code: str
    pay_period: str
    basic_salary: Decimal
    allowances: Decimal
    deductions: Decimal
    net_salary: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_date: Optional[date] = None
    payment_status: str

    model_config = {"from_attributes": True}


class PayrollDetailReport(BaseModel):
    items: List[PayrollDetailItem]
    total: int
    page: int
    limit: int
    pages: int
    summary: PayrollSummaryByPeriod
