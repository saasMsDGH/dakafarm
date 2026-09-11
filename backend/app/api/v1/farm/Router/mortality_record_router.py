"""
MortalityRecord router — HTTP endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.MortalityRecordSchema import (
    MortalityRecordCreate,
    MortalityRecordListResponse,
    MortalityRecordResponse,
    MortalityRecordUpdate,
)
from app.api.v1.farm.service.MortalityRecordService import MortalityRecordService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# ── RBAC role checkers ─────────────────────────────────────────────────────────
create_record = RoleChecker(["admin", "Farm Manager", "Farm Worker"])
manage_record = RoleChecker(["admin", "Farm Manager"])
admin_only = RoleChecker(["admin"])

# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/mortality-records",
    tags=["Mortality Records"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=MortalityRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new mortality record",
)
async def create_record_endpoint(
    request: MortalityRecordCreate,
    current_user: Users = Depends(create_record),
    db: AsyncSession = Depends(get_db),
) -> MortalityRecordResponse:
    return await MortalityRecordService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=MortalityRecordListResponse,
    summary="List all mortality records",
)
async def list_records_endpoint(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term"),
    sort_by: str = Query(default="record_date", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MortalityRecordListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await MortalityRecordService.list_records(db, params)


@router.get(
    "/{record_id}",
    response_model=MortalityRecordResponse,
    summary="Get a single mortality record",
)
async def get_record_endpoint(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MortalityRecordResponse:
    return await MortalityRecordService.get_record(db, record_id)


@router.put(
    "/{record_id}",
    response_model=MortalityRecordResponse,
    summary="Update a mortality record (managers only)",
)
async def update_record_endpoint(
    record_id: int,
    request: MortalityRecordUpdate,
    current_user: Users = Depends(manage_record),
    db: AsyncSession = Depends(get_db),
) -> MortalityRecordResponse:
    return await MortalityRecordService.update(db, record_id, request)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a mortality record (admin only)",
)
async def delete_record_endpoint(
    record_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await MortalityRecordService.delete(db, record_id)
