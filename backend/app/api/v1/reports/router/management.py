from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.management import ManagementReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

mgmt_access = RoleChecker(["admin", "Chairperson", "finance_manager"])
cust_access = RoleChecker(["admin", "Chairperson", "finance_manager", "sell_manager", "sell_officer"])
sup_access = RoleChecker(["admin", "Chairperson", "finance_manager", "Accountant"])

router = APIRouter(prefix="/management", tags=["Reports - Management"])


@router.get("/farm-summary")
async def farm_summary(
    date_from: str = Query(..., description="YYYY-MM-DD"),
    date_to: str = Query(..., description="YYYY-MM-DD"),
    current_user: Users = Depends(mgmt_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.farm_summary(db, date_from, date_to)


@router.get("/monthly")
async def monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    current_user: Users = Depends(mgmt_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.monthly_report(db, year)


@router.get("/customers/list")
async def customers_list(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500), search: Optional[str] = None,
    current_user: Users = Depends(cust_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await ManagementReportService.customers_list(db, params)


@router.get("/customers/sales")
async def customers_sales(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(cust_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.customers_sales(db, date_from, date_to)


@router.get("/customers/outstanding")
async def customers_outstanding(
    current_user: Users = Depends(cust_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.customers_outstanding(db)


@router.get("/suppliers/list")
async def suppliers_list(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500), search: Optional[str] = None,
    current_user: Users = Depends(sup_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await ManagementReportService.suppliers_list(db, params)


@router.get("/suppliers/purchases")
async def suppliers_purchases(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(sup_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.suppliers_purchases(db, date_from, date_to)


@router.get("/suppliers/outstanding")
async def suppliers_outstanding(
    current_user: Users = Depends(sup_access), db: AsyncSession = Depends(get_db),
):
    return await ManagementReportService.suppliers_outstanding(db)
