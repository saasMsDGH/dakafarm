from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

class AccountType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    MOBILE_MONEY = "MOBILE_MONEY"

class FinancialAccountCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    account_type: AccountType
    bank_name: Optional[str] = Field(None, max_length=150)
    account_number: Optional[str] = Field(None, max_length=100)
    opening_balance: Optional[Decimal] = Field(Decimal('0.00'), ge=0)
    is_active: Optional[bool] = True

class FinancialAccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    account_type: Optional[AccountType] = None
    bank_name: Optional[str] = Field(None, max_length=150)
    account_number: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class FinancialAccountResponse(BaseModel):
    id: int
    name: str
    account_type: str
    bank_name: Optional[str]
    account_number: Optional[str]
    opening_balance: Decimal
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FinancialAccountListResponse(BaseModel):
    items: List[FinancialAccountResponse]
    total: int
    page: int
    limit: int
    pages: int
