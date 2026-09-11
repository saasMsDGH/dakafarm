"""
FeedRecord router — HTTP endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.FeedRecordSchema import (
    FeedRecordCreate,
    FeedRecordListResponse,
    FeedRecordResponse,
    FeedRecordUpdate,
)
from app.api.v1.farm.service.FeedRecordService import FeedRecordService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# ── RBAC role checkers ─────────────────────────────────────────────────────────
# Operational workers CAN create feed records
create_record = RoleChecker(["admin", "Farm Manager", "Farm Worker"])
# But only managers/admins can update/delete mistakes
manage_record = RoleChecker(["admin", "Farm Manager"])
admin_only = RoleChecker(["admin"])

# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/feed-records",
    tags=["Feed Records"],
    redirect_slashes=False,
)


@router.post(
    "/",
    response_model=FeedRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new feed record",
)
async def create_record_endpoint(
    request: FeedRecordCreate,
    current_user: Users = Depends(create_record),
    db: AsyncSession = Depends(get_db),
) -> FeedRecordResponse:
    return await FeedRecordService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=FeedRecordListResponse,
    summary="List all feed records",
)
async def list_records_endpoint(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term (currently limited for this module)"),
    sort_by: str = Query(default="record_date", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedRecordListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await FeedRecordService.list_records(db, params)


@router.get(
    "/{record_id}",
    response_model=FeedRecordResponse,
    summary="Get a single feed record",
)
async def get_record_endpoint(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedRecordResponse:
    return await FeedRecordService.get_record(db, record_id)


@router.put(
    "/{record_id}",
    response_model=FeedRecordResponse,
    summary="Update a feed record (managers only)",
)
async def update_record_endpoint(
    record_id: int,
    request: FeedRecordUpdate,
    current_user: Users = Depends(manage_record),
    db: AsyncSession = Depends(get_db),
) -> FeedRecordResponse:
    return await FeedRecordService.update(db, record_id, request, current_user.id)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a feed record (admin only)",
)
async def delete_record_endpoint(
    record_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await FeedRecordService.delete(db, record_id, current_user.id)
