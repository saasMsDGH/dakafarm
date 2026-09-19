from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class RevenueSection(BaseModel):
    sales: Decimal
    total_revenue: Decimal

class COGSSection(BaseModel):
    purchases: Decimal
    total_cogs: Decimal

class OPEXSection(BaseModel):
    direct_expenses: Decimal
    payroll: Decimal
    negative_adjustments: Decimal
    total_opex: Decimal

class NonOperatingSection(BaseModel):
    other_income: Decimal
    positive_adjustments: Decimal
    uncategorized_income: Decimal
    uncategorized_expense: Decimal
    total_non_operating: Decimal

class PnLResponse(BaseModel):
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    revenue: RevenueSection
    cogs: COGSSection
    gross_profit: Decimal
    
    opex: OPEXSection
    operating_profit: Decimal
    
    non_operating: NonOperatingSection
    net_profit: Decimal
