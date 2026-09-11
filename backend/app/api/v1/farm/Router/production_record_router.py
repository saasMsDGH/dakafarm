"""
ProductionRecord router — HTTP endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.ProductionRecordSchema import (
    ProductionRecordCreate,
    ProductionRecordListResponse,
    ProductionRecordResponse,
    ProductionRecordUpdate,
)
from app.api.v1.farm.service.ProductionRecordService import ProductionRecordService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# ── RBAC role checkers ─────────────────────────────────────────────────────────
# Operational workers CAN create daily production records
create_record = RoleChecker(["admin", "Farm Manager", "Farm Worker"])
# Only managers/admins can update/delete mistakes
manage_record = RoleChecker(["admin", "Farm Manager"])
admin_only = RoleChecker(["admin"])

# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/production-records",
    tags=["Production Records"],
    redirect_slashes=False,
)


@router.post(
    "/",
    response_model=ProductionRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new production record",
)
async def create_record_endpoint(
    request: ProductionRecordCreate,
    current_user: Users = Depends(create_record),
    db: AsyncSession = Depends(get_db),
) -> ProductionRecordResponse:
    return await ProductionRecordService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=ProductionRecordListResponse,
    summary="List all production records",
)
async def list_records_endpoint(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term (currently limited)"),
    sort_by: str = Query(default="record_date", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductionRecordListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await ProductionRecordService.list_records(db, params)


@router.get(
    "/{record_id}",
    response_model=ProductionRecordResponse,
    summary="Get a single production record",
)
async def get_record_endpoint(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductionRecordResponse:
    return await ProductionRecordService.get_record(db, record_id)


@router.put(
    "/{record_id}",
    response_model=ProductionRecordResponse,
    summary="Update a production record (managers only)",
)
async def update_record_endpoint(
    record_id: int,
    request: ProductionRecordUpdate,
    current_user: Users = Depends(manage_record),
    db: AsyncSession = Depends(get_db),
) -> ProductionRecordResponse:
    return await ProductionRecordService.update(db, record_id, request)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a production record (admin only)",
)
async def delete_record_endpoint(
    record_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ProductionRecordService.delete(db, record_id)
