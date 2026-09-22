from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class FinancialOverview(BaseModel):
    total_sales: Decimal
    total_purchases: Decimal
    total_expenses: Decimal
    total_payroll: Decimal
    net_profit: Decimal

class CashPosition(BaseModel):
    cash: Decimal
    bank: Decimal
    mobile_money: Decimal
    total_available: Decimal

class FarmOperations(BaseModel):
    total_birds: int
    eggs_produced: int
    mortality_rate: str
    feed_used: str
    vaccinations_due: int
    low_stock_items: int

class CustomersSuppliers(BaseModel):
    customer_outstanding: Decimal
    supplier_payable: Decimal
    active_customers: int
    active_suppliers: int

class FarmOperationsReport(BaseModel):
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    generated_on: datetime
    
    financial_overview: FinancialOverview
    cash_position: CashPosition
    farm_operations: FarmOperations
    customers_suppliers: CustomersSuppliers
