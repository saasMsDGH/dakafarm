from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.sales import SalesReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

sales_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson", "sell_manager", "sell_officer"])

router = APIRouter(prefix="/sales", tags=["Reports - Sales"])


@router.get("/summary")
async def sales_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    customer_id: Optional[int] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    return await SalesReportService.get_summary(db, date_from, date_to, customer_id, payment_status)


@router.get("/detail")
async def sales_detail(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=500),
    search: Optional[str] = None, sort_by: str = "sale_date", order: str = "desc",
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    customer_id: Optional[int] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await SalesReportService.get_detail(db, params, date_from, date_to, customer_id, payment_status)


@router.get("/by-product")
async def sales_by_product(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    return await SalesReportService.by_product(db, date_from, date_to)


@router.get("/by-customer")
async def sales_by_customer(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    return await SalesReportService.by_customer(db, date_from, date_to)


@router.get("/by-category")
async def sales_by_category(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    return await SalesReportService.by_category(db, date_from, date_to)


@router.get("/payment-status")
async def sales_payment_status(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(sales_access), db: AsyncSession = Depends(get_db),
):
    return await SalesReportService.payment_status(db, date_from, date_to)
