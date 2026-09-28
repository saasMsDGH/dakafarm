"""
Pydantic schemas for the FinancialTransaction resource.

Design notes:
  - TransactionType and Direction enums live here (schema layer), not in the DB model.
    This matches every other module in the project (see AccountSchema.AccountType).
  - No update schema is provided — transactions are immutable after posting.
  - amount is validated gt=0 (strictly positive).
  - direction must be IN or OUT.
  - account_id is required on create.
  - transaction_date defaults to now() via the database; the API client may supply
    a specific date for historical entry (e.g. back-dating last month's expense).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from app.api.v1.finance.schemas.AccountSchema import FinancialAccountResponse

# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------

class TransactionType(str, Enum):
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    EXPENSE = "EXPENSE"
    PAYROLL = "PAYROLL"
    ASSET_PURCHASE = "ASSET_PURCHASE"
    OWNER_INVESTMENT = "OWNER_INVESTMENT"
    OTHER_INCOME = "OTHER_INCOME"
    ADJUSTMENT = "ADJUSTMENT"


class Direction(str, Enum):
    IN = "IN"
    OUT = "OUT"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class FinancialTransactionCreate(BaseModel):
    account_id: int = Field(..., description="ID of the financial account affected")
    transaction_type: TransactionType = Field(..., description="Type of financial event")
    direction: Direction = Field(..., description="IN = money received, OUT = money paid")
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2,
                            description="Transaction amount — always positive")
    description: Optional[str] = Field(
        None, max_length=500, description="Explanation of the transaction"
    )
    reference_number: Optional[str] = Field(
        None, max_length=100,
        description="External/internal reference (invoice no, payroll ID, etc.)"
    )
    transaction_date: Optional[datetime] = Field(
        None,
        description="When the event occurred (defaults to now if omitted)"
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FinancialTransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_date: datetime
    transaction_type: str
    direction: str
    amount: Decimal
    description: Optional[str]
    reference_number: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    account: Optional[FinancialAccountResponse] = None

    model_config = {"from_attributes": True}


class FinancialTransactionListResponse(BaseModel):
    items: List[FinancialTransactionResponse]
    total: int
    page: int
    limit: int
    pages: int
