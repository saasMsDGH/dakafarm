from __future__ import annotations
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class FarmManagementSummary(BaseModel):
    period_from: str
    period_to: str
    # Financial
    total_money_in: Decimal
    total_money_out: Decimal
    net_movement: Decimal
    # Sales
    total_sales_amount: Decimal
    sales_paid: Decimal
    sales_outstanding: Decimal
    # Purchases
    total_purchases_amount: Decimal
    purchases_paid: Decimal
    purchases_outstanding: Decimal
    # Expenses
    total_expenses_amount: Decimal
    expenses_paid: Decimal
    expenses_outstanding: Decimal
    # Production
    total_eggs: int
    good_eggs: int
    damaged_eggs: int
    avg_laying_pct: Optional[Decimal] = None
    # Farm
    active_flocks: int
    total_birds: int
    total_mortality: int
    # Inventory
    total_products: int
    low_stock_items: int
    out_of_stock_items: int
    # HR
    total_employees: int
    payroll_paid: Decimal
    payroll_outstanding: Decimal


class MonthlyReportItem(BaseModel):
    month: str  # YYYY-MM
    sales_amount: Decimal
    purchases_amount: Decimal
    expenses_amount: Decimal
    money_in: Decimal
    money_out: Decimal
    egg_production: int
    mortality: int
    payroll_net: Decimal


class MonthlyManagementReport(BaseModel):
    year: int
    items: List[MonthlyReportItem]


class CustomerListItem(BaseModel):
    id: int
    customer_code: str
    name: str
    business_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Decimal

    model_config = {"from_attributes": True}


class CustomerSalesItem(BaseModel):
    customer_id: int
    customer_name: str
    num_sales: int
    total_sales: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class CustomerOutstandingItem(BaseModel):
    customer_id: int
    customer_name: str
    sale_id: int
    invoice_number: str
    sale_date: str
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_status: str


class SupplierListItem(BaseModel):
    id: int
    supplier_code: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    model_config = {"from_attributes": True}


class SupplierPurchasesItem(BaseModel):
    supplier_id: int
    supplier_name: str
    num_purchases: int
    total_purchases: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class SupplierOutstandingItem(BaseModel):
    supplier_id: int
    supplier_name: str
    purchase_id: int
    purchase_number: str
    purchase_date: str
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_status: str
