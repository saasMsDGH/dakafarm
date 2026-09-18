from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.schemas.AccountSchema import (
    FinancialAccountCreate,
    FinancialAccountListResponse,
    FinancialAccountResponse,
    FinancialAccountUpdate,
)
from app.api.v1.finance.service.AccountService import AccountService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/accounts",
    tags=["Financial Accounts"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=FinancialAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new financial account"
)
async def create_account(
    request: FinancialAccountCreate,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialAccountResponse:
    return await AccountService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=FinancialAccountListResponse,
    summary="List financial accounts"
)
async def list_accounts(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    account_type: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialAccountListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await AccountService.list_accounts(db, params, account_type)

@router.get(
    "/{account_id}",
    response_model=FinancialAccountResponse,
    summary="Get a financial account by ID"
)
async def get_account(
    account_id: int,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialAccountResponse:
    return await AccountService.get_account(db, account_id)

@router.put(
    "/{account_id}",
    response_model=FinancialAccountResponse,
    summary="Update a financial account"
)
async def update_account(
    account_id: int,
    request: FinancialAccountUpdate,
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinancialAccountResponse:
    return await AccountService.update(db, account_id, request)
