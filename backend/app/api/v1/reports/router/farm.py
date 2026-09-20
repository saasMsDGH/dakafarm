from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.farm import FarmReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

farm_access = RoleChecker(["admin", "Farm Manager", "Chairperson"])

router = APIRouter(prefix="/farm", tags=["Reports - Farm"])


@router.get("/production-summary")
async def production_summary(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    flock_id: Optional[int] = None, house_id: Optional[int] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit)
    return await FarmReportService.production_summary(db, params, flock_id, house_id, date_from, date_to)


@router.get("/production-by-flock")
async def production_by_flock(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.production_by_flock(db, date_from, date_to)


@router.get("/production-by-house")
async def production_by_house(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.production_by_house(db, date_from, date_to)


@router.get("/feed-usage")
async def feed_usage(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    flock_id: Optional[int] = None, product_id: Optional[int] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit)
    return await FarmReportService.feed_usage(db, params, flock_id, product_id, date_from, date_to)


@router.get("/feed-by-flock")
async def feed_by_flock(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.feed_by_flock(db, date_from, date_to)


@router.get("/medication")
async def medication(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    flock_id: Optional[int] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit)
    return await FarmReportService.medication(db, params, flock_id, date_from, date_to)


@router.get("/vaccination")
async def vaccination(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    flock_id: Optional[int] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit)
    return await FarmReportService.vaccination(db, params, flock_id, date_from, date_to)


@router.get("/upcoming-vaccinations")
async def upcoming_vaccinations(
    days_ahead: int = Query(30, ge=1, le=365),
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.upcoming_vaccinations(db, days_ahead)


@router.get("/mortality-summary")
async def mortality_summary(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.mortality_summary(db, date_from, date_to)


@router.get("/mortality-by-flock")
async def mortality_by_flock(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.mortality_by_flock(db, date_from, date_to)


@router.get("/mortality-by-cause")
async def mortality_by_cause(
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(farm_access), db: AsyncSession = Depends(get_db),
):
    return await FarmReportService.mortality_by_cause(db, date_from, date_to)
