from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class TrialBalanceEntry(BaseModel):
    account_name: str
    debit: Decimal
    credit: Decimal

class TrialBalanceResponse(BaseModel):
    entries: List[TrialBalanceEntry]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool
    as_of_date: datetime
