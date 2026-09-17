from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# --- Request Schemas ---

class PayrollCreate(BaseModel):
    employee_id: int = Field(..., description="ID of the employee")
    pay_period: str = Field(..., max_length=50, description="e.g. September 2026")
    basic_salary: Decimal = Field(..., ge=0)
    allowances: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    deductions: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    payment_date: Optional[date] = None
    payment_status: Optional[str] = Field("Pending", max_length=50)

class PayrollUpdate(BaseModel):
    pay_period: Optional[str] = Field(None, max_length=50)
    basic_salary: Optional[Decimal] = Field(None, ge=0)
    allowances: Optional[Decimal] = Field(None, ge=0)
    deductions: Optional[Decimal] = Field(None, ge=0)
    payment_date: Optional[date] = None
    payment_status: Optional[str] = Field(None, max_length=50)

# --- Response Schemas ---

class EmployeeBrief(BaseModel):
    first_name: str
    last_name: str
    position: str

    model_config = {"from_attributes": True}

class PayrollResponse(BaseModel):
    id: int
    employee_id: int
    pay_period: str
    basic_salary: Decimal
    allowances: Decimal
    deductions: Decimal
    net_salary: Decimal
    payment_date: Optional[date]
    payment_status: str
    
    employee: Optional[EmployeeBrief] = None
    
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PayrollListResponse(BaseModel):
    items: List[PayrollResponse]
    total: int
    page: int
    limit: int
    pages: int
