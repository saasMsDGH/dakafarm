from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.service.inventory import InventoryReportService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

inventory_access = RoleChecker(["admin", "finance_manager", "Accountant", "Chairperson", "Farm Manager", "inventory_admin"])

router = APIRouter(prefix="/inventory", tags=["Reports - Inventory"])


@router.get("/current-stock")
async def current_stock(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None, category_id: Optional[int] = None,
    current_user: Users = Depends(inventory_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit, search=search)
    return await InventoryReportService.current_stock(db, params, category_id)


@router.get("/stock-movements")
async def stock_movements(
    page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500),
    product_id: Optional[int] = None, movement_type: Optional[str] = None,
    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    current_user: Users = Depends(inventory_access), db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, limit=limit)
    return await InventoryReportService.stock_movements(db, params, product_id, movement_type, date_from, date_to)


@router.get("/low-stock")
async def low_stock(
    current_user: Users = Depends(inventory_access), db: AsyncSession = Depends(get_db),
):
    return await InventoryReportService.low_stock(db)


@router.get("/valuation")
async def inventory_valuation(
    current_user: Users = Depends(inventory_access), db: AsyncSession = Depends(get_db),
):
    return await InventoryReportService.valuation(db)
