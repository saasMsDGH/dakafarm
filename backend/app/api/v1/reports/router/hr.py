from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.hr import HRReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

hr_access = RoleChecker(["admin", "hr_manager", "hr_officer", "finance_manager", "Accountant", "Chairperson"])

router = APIRouter(prefix="/hr", tags=["Reports - HR"])


@router.get("/employees")
async def employees(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    current_user: Users = Depends(hr_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await HRReportService.employees(db, params)


@router.get("/payroll-summary")
async def payroll_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(hr_access), db: AsyncSession = Depends(get_db),
):
    return await HRReportService.payroll_summary(db, date_from, date_to)


@router.get("/payroll-detail")
async def payroll_detail(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, pay_period: Optional[str] = None,
    employee_id: Optional[int] = None,
    current_user: Users = Depends(hr_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await HRReportService.payroll_detail(db, params, pay_period, employee_id)
