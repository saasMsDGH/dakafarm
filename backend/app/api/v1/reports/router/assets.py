from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.assets import AssetsReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

assets_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson"])

router = APIRouter(prefix="/assets", tags=["Reports - Assets"])


@router.get("/register")
async def asset_register(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, status: Optional[str] = None, condition: Optional[str] = None,
    current_user: Users = Depends(assets_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await AssetsReportService.register(db, params, status, condition)


@router.get("/by-condition")
async def assets_by_condition(
    current_user: Users = Depends(assets_access), db: AsyncSession = Depends(get_db),
):
    return await AssetsReportService.by_condition(db)
