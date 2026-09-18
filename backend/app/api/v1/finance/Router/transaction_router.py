"""
transaction_router — HTTP endpoints for FinancialTransaction.

Exposed endpoints (Phase 2):
  POST   /api/v1/finance/transactions/        Create a transaction
  GET    /api/v1/finance/transactions/        List with filter/sort/paginate
  GET    /api/v1/finance/transactions/{id}    Get single transaction

No PUT or DELETE — transactions are immutable after posting.
All endpoints require finance_manager or admin role.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.schemas.TransactionSchema import (
    FinancialTransactionCreate,
    FinancialTransactionListResponse,
    FinancialTransactionResponse,
)
from app.api.v1.finance.service.TransactionService import TransactionService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/transactions",
    tags=["Financial Transactions"],
    redirect_slashes=False,
)


@router.post(
    "/",
    response_model=FinancialTransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a new financial transaction",
)
async def create_transaction(
    request: FinancialTransactionCreate,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialTransactionResponse:
    return await TransactionService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=FinancialTransactionListResponse,
    summary="List financial transactions with filtering and pagination",
)
async def list_transactions(
    # Pagination
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None, description="Search description or reference_number"),
    sort_by: str = Query(default="transaction_date"),
    order: str = Query(default="desc"),
    # Filters
    account_id: Optional[int] = Query(default=None, description="Filter by financial account ID"),
    transaction_type: Optional[str] = Query(default=None, description="Filter by type (SALE, EXPENSE, ...)"),
    direction: Optional[str] = Query(default=None, description="Filter by direction: IN or OUT"),
    date_from: Optional[datetime] = Query(default=None, description="Start of date range (ISO 8601)"),
    date_to: Optional[datetime] = Query(default=None, description="End of date range (ISO 8601)"),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialTransactionListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await TransactionService.list_transactions(
        db,
        params,
        account_id=account_id,
        transaction_type=transaction_type,
        direction=direction,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/{transaction_id}",
    response_model=FinancialTransactionResponse,
    summary="Get a single financial transaction by ID",
)
async def get_transaction(
    transaction_id: int,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialTransactionResponse:
    return await TransactionService.get_transaction(db, transaction_id)
