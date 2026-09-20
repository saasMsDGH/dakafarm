from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.expenses import ExpensesReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

expenses_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson"])

router = APIRouter(prefix="/expenses", tags=["Reports - Expenses"])


@router.get("/summary")
async def expenses_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    category: Optional[str] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(expenses_access), db: AsyncSession = Depends(get_db),
):
    return await ExpensesReportService.get_summary(db, date_from, date_to, category, payment_status)


@router.get("/detail")
async def expenses_detail(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=500),
    search: Optional[str] = None, sort_by: str = "expense_date", order: str = "desc",
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    category: Optional[str] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(expenses_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await ExpensesReportService.get_detail(db, params, date_from, date_to, category, payment_status)


@router.get("/by-category")
async def expenses_by_category(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(expenses_access), db: AsyncSession = Depends(get_db),
):
    return await ExpensesReportService.by_category(db, date_from, date_to)
