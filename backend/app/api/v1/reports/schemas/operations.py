from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class FinancialOverview(BaseModel):
    total_sales: Decimal
    total_purchases: Decimal
    total_cogs: Decimal
    gross_profit: Decimal
    gross_margin: str
    total_expenses: Decimal
    total_payroll: Decimal
    total_operating_costs: Decimal
    net_profit: Decimal
    net_profit_margin: str

class CashPosition(BaseModel):
    cash: Decimal
    bank: Decimal
    mobile_money: Decimal
    total_available: Decimal
    customer_outstanding: Decimal
    supplier_payable: Decimal
    net_working_capital: Decimal
    liquidity_status: str

class FarmOperations(BaseModel):
    total_flocks: int
    active_flocks: int
    total_birds: int
    initial_birds: int
    total_mortality: int
    mortality_rate: str
    eggs_produced: int
    good_eggs: int
    damaged_eggs: int
    egg_breakage_rate: str
    average_laying_rate: str
    feed_used: str
    feed_used_kg: Decimal
    feed_cost: Decimal
    vaccinations_due: int
    active_houses: int
    total_capacity: int
    capacity_utilization: str
    low_stock_items: int

class CriticalStockItem(BaseModel):
    name: str
    unit_of_measure: str
    current_stock: Decimal
    reorder_level: Decimal
    unit_price: Decimal
    stock_value: Decimal
    status: str

class InventorySummary(BaseModel):
    total_skus: int
    total_valuation: Decimal
    low_stock_count: int
    out_of_stock_count: int
    stock_health_rate: str
    critical_items: List[CriticalStockItem] = []

class AssetSummary(BaseModel):
    total_assets_count: int
    total_quantity: int
    total_asset_cost: Decimal
    total_paid: Decimal
    total_payable: Decimal
    good_condition_count: int
    fair_or_poor_count: int
    in_maintenance_count: int

class HRSummary(BaseModel):
    total_staff: int
    active_staff: int
    total_basic_salary: Decimal
    total_allowances: Decimal
    total_deductions: Decimal
    net_payroll_liability: Decimal
    paid_payroll: Decimal
    pending_payroll: Decimal

class CustomersSuppliers(BaseModel):
    customer_outstanding: Decimal
    supplier_payable: Decimal
    active_customers: int
    active_suppliers: int

class ExecutiveKPIs(BaseModel):
    profit_margin_status: str
    cash_flow_health: str
    laying_performance: str
    mortality_alert_level: str
    inventory_risk: str

class FarmOperationsReport(BaseModel):
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    generated_on: datetime
    report_reference: str
    
    financial_overview: FinancialOverview
    cash_position: CashPosition
    farm_operations: FarmOperations
    inventory_summary: InventorySummary
    asset_summary: AssetSummary
    hr_summary: HRSummary
    customers_suppliers: CustomersSuppliers
    executive_kpis: ExecutiveKPIs
