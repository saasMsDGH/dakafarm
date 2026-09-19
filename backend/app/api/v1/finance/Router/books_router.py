from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.schemas.BookSchema import BookResponse
from app.api.v1.finance.service.BookService import BookService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/books",
    tags=["Finance Books"],
    redirect_slashes=False,
)

@router.get(
    "/cash",
    response_model=BookResponse,
    summary="Get Cash Book for a specific CASH account",
)
async def get_cash_book(
    account_id: int = Query(..., description="ID of the CASH account to report on"),
    # Pagination
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None, description="Search description or reference_number"),
    # Filtering
    date_from: Optional[datetime] = Query(default=None, description="Start date (ISO 8601)"),
    date_to: Optional[datetime] = Query(default=None, description="End date (ISO 8601)"),
    transaction_type: Optional[str] = Query(default=None),
    direction: Optional[str] = Query(default=None, description="IN or OUT"),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    params = PaginationParams(page=page, limit=limit, search=search)
    return await BookService.get_book(
        db=db,
        expected_type="CASH",
        account_id=account_id,
        params=params,
        date_from=date_from,
        date_to=date_to,
        transaction_type=transaction_type,
        direction=direction
    )

@router.get(
    "/bank",
    response_model=BookResponse,
    summary="Get Bank Book for a specific BANK account",
)
async def get_bank_book(
    account_id: int = Query(..., description="ID of the BANK account to report on"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    transaction_type: Optional[str] = Query(default=None),
    direction: Optional[str] = Query(default=None),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    params = PaginationParams(page=page, limit=limit, search=search)
    return await BookService.get_book(db, "BANK", account_id, params, date_from, date_to, transaction_type, direction)

@router.get(
    "/mobile-money",
    response_model=BookResponse,
    summary="Get Mobile Money Book for a specific MOBILE_MONEY account",
)
async def get_mobile_money_book(
    account_id: int = Query(..., description="ID of the MOBILE_MONEY account to report on"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=500),
    search: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    transaction_type: Optional[str] = Query(default=None),
    direction: Optional[str] = Query(default=None),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    params = PaginationParams(page=page, limit=limit, search=search)
    return await BookService.get_book(db, "MOBILE_MONEY", account_id, params, date_from, date_to, transaction_type, direction)
