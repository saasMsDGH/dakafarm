from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AssetsSection(BaseModel):
    cash_and_bank: Decimal
    accounts_receivable: Decimal
    prepaid_purchases: Decimal
    fixed_assets: Decimal
    total_assets: Decimal

class LiabilitiesSection(BaseModel):
    accounts_payable: Decimal
    unearned_revenue: Decimal
    total_liabilities: Decimal

class EquitySection(BaseModel):
    owner_capital: Decimal
    retained_earnings: Decimal
    total_equity: Decimal

class BalanceSheetResponse(BaseModel):
    as_of_date: Optional[datetime]
    
    assets: AssetsSection
    liabilities: LiabilitiesSection
    equity: EquitySection
    
    is_balanced: bool
