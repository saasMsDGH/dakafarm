"""
MedicationRecord router — HTTP endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.MedicationRecordSchema import (
    MedicationRecordCreate,
    MedicationRecordListResponse,
    MedicationRecordResponse,
    MedicationRecordUpdate,
)
from app.api.v1.farm.service.MedicationRecordService import MedicationRecordService
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
    prefix="/medication-records",
    tags=["Medication Records"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=MedicationRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medication record",
)
async def create_record_endpoint(
    request: MedicationRecordCreate,
    current_user: Users = Depends(create_record),
    db: AsyncSession = Depends(get_db),
) -> MedicationRecordResponse:
    return await MedicationRecordService.create(db, request, current_user.id)


@router.get(
    "/",
    response_model=MedicationRecordListResponse,
    summary="List all medication records",
)
async def list_records_endpoint(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search term"),
    sort_by: str = Query(default="record_date", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MedicationRecordListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await MedicationRecordService.list_records(db, params)


@router.get(
    "/{record_id}",
    response_model=MedicationRecordResponse,
    summary="Get a single medication record",
)
async def get_record_endpoint(
    record_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MedicationRecordResponse:
    return await MedicationRecordService.get_record(db, record_id)


@router.put(
    "/{record_id}",
    response_model=MedicationRecordResponse,
    summary="Update a medication record (managers only)",
)
async def update_record_endpoint(
    record_id: int,
    request: MedicationRecordUpdate,
    current_user: Users = Depends(manage_record),
    db: AsyncSession = Depends(get_db),
) -> MedicationRecordResponse:
    return await MedicationRecordService.update(db, record_id, request, current_user.id)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medication record (admin only)",
)
async def delete_record_endpoint(
    record_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await MedicationRecordService.delete(db, record_id, current_user.id)
