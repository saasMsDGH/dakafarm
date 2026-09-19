from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OperatingFlows(BaseModel):
    cash_from_sales: Decimal
    cash_to_suppliers: Decimal
    cash_for_expenses: Decimal
    cash_for_payroll: Decimal
    other_operating_cash: Decimal
    uncategorized_operating_cash: Decimal
    net_operating_cash_flow: Decimal

class InvestingFlows(BaseModel):
    cash_for_assets: Decimal
    net_investing_cash_flow: Decimal

class FinancingFlows(BaseModel):
    owner_investments: Decimal
    net_financing_cash_flow: Decimal

class CashFlowResponse(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    operating: OperatingFlows
    investing: InvestingFlows
    financing: FinancingFlows
    
    net_change_in_cash: Decimal
    opening_balance: Decimal
    ending_balance: Decimal
