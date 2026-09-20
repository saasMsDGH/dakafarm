from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class FlockSummary(BaseModel):
    total_birds: int
    active_flocks: int
    total_mortality: int
    sick_birds: int

class HealthSummary(BaseModel):
    medication_cost: Decimal
    vaccines_used: Decimal

class ProductionSummary(BaseModel):
    total_quantity: Decimal

class HRSummary(BaseModel):
    total_employees: int
    payroll_total: Decimal

class FinanceSummary(BaseModel):
    revenue: Decimal
    expenses: Decimal
    net_profit: Decimal

class AssetsSummary(BaseModel):
    total_active_assets: int
    asset_value: Decimal

class FarmOperationsReport(BaseModel):
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    flocks: FlockSummary
    health: HealthSummary
    production: ProductionSummary
    hr: HRSummary
    finance: FinanceSummary
    assets: AssetsSummary
