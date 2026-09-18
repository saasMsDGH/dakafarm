from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.schemas.ReceivablesPayablesSchema import (
    ReceivablesSummaryResponse,
    CustomerReceivablesDetailResponse,
    PayablesSummaryResponse,
    SupplierPayablesDetailResponse
)
from app.api.v1.finance.service.ReceivablesPayablesService import ReceivablesPayablesService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

finance_manager = RoleChecker(["admin", "finance_manager"])

receivables_router = APIRouter(
    prefix="/receivables",
    tags=["Finance Receivables"],
    redirect_slashes=False,
)

payables_router = APIRouter(
    prefix="/payables",
    tags=["Finance Payables"],
    redirect_slashes=False,
)

# ----------------- RECEIVABLES -----------------
@receivables_router.get(
    "/customers",
    response_model=ReceivablesSummaryResponse,
    summary="List all customers with outstanding balances (Receivables)",
)
async def list_receivables_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None, description="Search by customer name or code"),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> ReceivablesSummaryResponse:
    params = PaginationParams(page=page, limit=limit, search=search)
    return await ReceivablesPayablesService.get_receivables_summary(db, params)

@receivables_router.get(
    "/customers/{customer_id}",
    response_model=CustomerReceivablesDetailResponse,
    summary="Get unpaid sales for a specific customer",
)
async def get_customer_receivables(
    customer_id: int,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> CustomerReceivablesDetailResponse:
    return await ReceivablesPayablesService.get_customer_receivables_detail(db, customer_id)


# ----------------- PAYABLES -----------------
@payables_router.get(
    "/suppliers",
    response_model=PayablesSummaryResponse,
    summary="List all suppliers with outstanding balances (Payables)",
)
async def list_payables_suppliers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None, description="Search by supplier name or code"),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> PayablesSummaryResponse:
    params = PaginationParams(page=page, limit=limit, search=search)
    return await ReceivablesPayablesService.get_payables_summary(db, params)

@payables_router.get(
    "/suppliers/{supplier_id}",
    response_model=SupplierPayablesDetailResponse,
    summary="Get unpaid purchases for a specific supplier",
)
async def get_supplier_payables(
    supplier_id: int,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> SupplierPayablesDetailResponse:
    return await ReceivablesPayablesService.get_supplier_payables_detail(db, supplier_id)
