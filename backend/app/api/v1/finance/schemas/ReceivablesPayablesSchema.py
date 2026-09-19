from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# --- RECEIVABLES (Customers owing us) ---

class OutstandingCustomerResponse(BaseModel):
    customer_id: int
    customer_code: str
    name: str
    phone: Optional[str]
    outstanding_balance: Decimal

class ReceivablesSummaryResponse(BaseModel):
    items: List[OutstandingCustomerResponse]
    total_outstanding: Decimal
    total: int
    page: int
    limit: int
    pages: int

class OutstandingSaleResponse(BaseModel):
    sale_id: int
    invoice_number: str
    sale_date: datetime
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal

class CustomerReceivablesDetailResponse(BaseModel):
    customer_id: int
    customer_name: str
    total_outstanding: Decimal
    sales: List[OutstandingSaleResponse]


# --- PAYABLES (Us owing Suppliers) ---

class OutstandingSupplierResponse(BaseModel):
    supplier_id: int
    supplier_code: str
    name: str
    phone: Optional[str]
    outstanding_balance: Decimal

class PayablesSummaryResponse(BaseModel):
    items: List[OutstandingSupplierResponse]
    total_outstanding: Decimal
    total: int
    page: int
    limit: int
    pages: int

class OutstandingPurchaseResponse(BaseModel):
    purchase_id: int
    purchase_number: str
    purchase_date: datetime
    total_amount: Decimal
    amount_paid: Decimal
    balance_due: Decimal

class SupplierPayablesDetailResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    total_outstanding: Decimal
    purchases: List[OutstandingPurchaseResponse]
