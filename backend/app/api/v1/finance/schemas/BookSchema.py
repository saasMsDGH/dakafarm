from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.api.v1.finance.schemas.AccountSchema import FinancialAccountResponse

class BookEntry(BaseModel):
    id: int
    transaction_date: datetime
    reference_number: Optional[str]
    description: Optional[str]
    transaction_type: str
    money_in: Decimal
    money_out: Decimal
    balance: Decimal

    model_config = {"from_attributes": True}

class BookPagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class BookResponse(BaseModel):
    account: FinancialAccountResponse
    opening_balance: Decimal
    items: List[BookEntry]
    total_money_in: Decimal
    total_money_out: Decimal
    closing_balance: Decimal
    pagination: BookPagination
