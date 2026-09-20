from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.purchases import PurchasesReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

purchases_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson"])

router = APIRouter(prefix="/purchases", tags=["Reports - Purchases"])


@router.get("/summary")
async def purchases_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    supplier_id: Optional[int] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(purchases_access), db: AsyncSession = Depends(get_db),
):
    return await PurchasesReportService.get_summary(db, date_from, date_to, supplier_id, payment_status)


@router.get("/detail")
async def purchases_detail(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=500),
    search: Optional[str] = None, sort_by: str = "purchase_date", order: str = "desc",
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    supplier_id: Optional[int] = None, payment_status: Optional[str] = None,
    current_user: Users = Depends(purchases_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search, sort_by=sort_by, order=order)
    return await PurchasesReportService.get_detail(db, params, date_from, date_to, supplier_id, payment_status)


@router.get("/by-supplier")
async def purchases_by_supplier(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(purchases_access), db: AsyncSession = Depends(get_db),
):
    return await PurchasesReportService.by_supplier(db, date_from, date_to)


@router.get("/by-product")
async def purchases_by_product(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(purchases_access), db: AsyncSession = Depends(get_db),
):
    return await PurchasesReportService.by_product(db, date_from, date_to)
