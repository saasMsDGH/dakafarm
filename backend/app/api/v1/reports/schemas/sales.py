from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class SalesSummary(BaseModel):
    total_sales: int
    total_amount: Decimal
    total_discount: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class SalesDetailItem(BaseModel):
    id: int
    invoice_number: str
    sale_date: datetime
    customer_name: Optional[str] = None
    subtotal: Decimal
    discount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    outstanding: Decimal
    payment_status: str
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}


class SalesDetailReport(BaseModel):
    items: List[SalesDetailItem]
    total: int
    page: int
    limit: int
    pages: int
    summary: SalesSummary


class SalesByProductItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str] = None
    quantity_sold: Decimal
    revenue: Decimal
    avg_selling_price: Decimal


class SalesByProductReport(BaseModel):
    items: List[SalesByProductItem]
    total_revenue: Decimal


class SalesByCustomerItem(BaseModel):
    customer_id: int
    customer_name: str
    business_type: Optional[str] = None
    num_sales: int
    total_sales: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class SalesByCustomerReport(BaseModel):
    items: List[SalesByCustomerItem]


class SalesByCategoryItem(BaseModel):
    category: str
    quantity: Decimal
    revenue: Decimal
    percentage: Decimal


class SalesByCategoryReport(BaseModel):
    items: List[SalesByCategoryItem]
    total_revenue: Decimal


class SalesPaymentStatusItem(BaseModel):
    payment_status: str
    num_sales: int
    total_value: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class SalesPaymentStatusReport(BaseModel):
    items: List[SalesPaymentStatusItem]
