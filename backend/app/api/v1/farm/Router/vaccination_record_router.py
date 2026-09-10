"""
VaccinationRecord router — HTTP endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.VaccinationRecordSchema import (
    VaccinationRecordCreate,
    VaccinationRecordListResponse,
    VaccinationRecordResponse,
    VaccinationRecordUpdate,
)
from app.api.v1.farm.service.VaccinationRecordService import VaccinationRecordService
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
    prefix="/vaccination-records",
    tags=["Vaccination Records"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=VaccinationRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vaccination record",
)
async def create_record_endpoint(
    request: VaccinationRecordCreate,
    current_user: Users = Depends(create_record),
    db: AsyncSession = Depends(get_db),
) -> VaccinationRecordResponse:
    return await VaccinationRecordService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=VaccinationRecordListResponse,
    summary="List all vaccination records",
)
async def list_records_endpoint(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term"),
    sort_by: str = Query(default="record_date", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VaccinationRecordListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await VaccinationRecordService.list_records(db, params)


@router.get(
    "/{record_id}",
    response_model=VaccinationRecordResponse,
    summary="Get a single vaccination record",
)
async def get_record_endpoint(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VaccinationRecordResponse:
    return await VaccinationRecordService.get_record(db, record_id)


@router.put(
    "/{record_id}",
    response_model=VaccinationRecordResponse,
    summary="Update a vaccination record (managers only)",
)
async def update_record_endpoint(
    record_id: int,
    request: VaccinationRecordUpdate,
    current_user: Users = Depends(manage_record),
    db: AsyncSession = Depends(get_db),
) -> VaccinationRecordResponse:
    return await VaccinationRecordService.update(db, record_id, request)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vaccination record (admin only)",
)
async def delete_record_endpoint(
    record_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await VaccinationRecordService.delete(db, record_id)
