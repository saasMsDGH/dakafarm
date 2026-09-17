from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.schemas.ExpenseSchema import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.api.v1.pos.service.ExpenseService import ExpenseService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

pos_manager = RoleChecker(["admin", "sell_manager"])
pos_officer = RoleChecker(["admin", "sell_manager", "sell_officer"])

router = APIRouter(
    prefix="/expenses",
    tags=["POS Expenses"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense record"
)
async def create_expense(
    request: ExpenseCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    return await ExpenseService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=ExpenseListResponse,
    summary="List expenses"
)
async def list_expenses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> ExpenseListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await ExpenseService.list_expenses(db, params, category)

@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get an expense by ID"
)
async def get_expense(
    expense_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    return await ExpenseService.get_expense(db, expense_id)

@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update an expense"
)
async def update_expense(
    expense_id: int,
    request: ExpenseUpdate,
    current_user: Users = Depends(pos_manager),
    db: AsyncSession = Depends(get_db),
) -> ExpenseResponse:
    return await ExpenseService.update(db, expense_id, request)

@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense"
)
async def delete_expense(
    expense_id: int,
    current_user: Users = Depends(pos_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ExpenseService.delete(db, expense_id)
