from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.financial import FinancialReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

finance_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson"])

router = APIRouter(prefix="/financial", tags=["Reports - Financial"])


@router.get("/transactions")
async def financial_transactions(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=500),
    search: Optional[str] = None, sort_by: str = "transaction_date", order: str = "desc",
    account_id: Optional[int] = None, account_type: Optional[str] = None,
    transaction_type: Optional[str] = None, direction: Optional[str] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await FinancialReportService.get_transaction_report(
        db, params, account_id=account_id, account_type=account_type,
        transaction_type=transaction_type, direction=direction, date_from=date_from, date_to=date_to,
    )


@router.get("/cash-book")
async def cash_book(
    account_id: int = Query(..., description="ID of the cash account"),
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, sort_by: str = "transaction_date", order: str = "asc",
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    transaction_type: Optional[str] = None, direction: Optional[str] = None,
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await FinancialReportService.get_book_report(
        db, account_id, params, date_from=date_from, date_to=date_to,
        transaction_type=transaction_type, direction=direction,
    )


@router.get("/bank-book")
async def bank_book(
    account_id: int = Query(..., description="ID of the bank account"),
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    transaction_type: Optional[str] = None, direction: Optional[str] = None,
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by="transaction_date", order="asc")
    return await FinancialReportService.get_book_report(
        db, account_id, params, date_from=date_from, date_to=date_to,
        transaction_type=transaction_type, direction=direction,
    )


@router.get("/mobile-book")
async def mobile_book(
    account_id: int = Query(..., description="ID of the mobile money account"),
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    transaction_type: Optional[str] = None, direction: Optional[str] = None,
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by="transaction_date", order="asc")
    return await FinancialReportService.get_book_report(
        db, account_id, params, date_from=date_from, date_to=date_to,
        transaction_type=transaction_type, direction=direction,
    )


@router.get("/account-summary")
async def account_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    account_type: Optional[str] = None,
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    return await FinancialReportService.get_account_summary(db, date_from, date_to, account_type)


@router.get("/daily-summary")
async def daily_summary(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: Users = Depends(finance_access), db: AsyncSession = Depends(get_db),
):
    return await FinancialReportService.get_daily_summary(db, date)
