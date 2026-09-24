

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.FlockSchema import (
    FlockCreate,
    FlockListResponse,
    FlockResponse,
    FlockUpdate,
)
from app.api.v1.farm.service.FlockService import FlockService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# ── RBAC role checkers ─────────────────────────────────────────────────────────
manage_flock = RoleChecker(["admin", "Farm Manager"])
admin_only = RoleChecker(["admin"])

# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/flocks",
    tags=["Flocks"],
    redirect_slashes=False,
)


@router.post(
    "/",
    response_model=FlockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new flock",
)
async def create_flock(
    request: FlockCreate,
    current_user: Users = Depends(manage_flock),
    db: AsyncSession = Depends(get_db),
) -> FlockResponse:
    return await FlockService.create_flock(db, request, current_user.id)


@router.get(
    "/",
    response_model=FlockListResponse,
    summary="List all flocks (paginated)",
)
async def list_flocks(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search by code, breed or status"),
    sort_by: str = Query(default="created_at", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlockListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await FlockService.list_flocks(db, params)


@router.get(
    "/{flock_id}",
    response_model=FlockResponse,
    summary="Get a single flock by ID",
)
async def get_flock(
    flock_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlockResponse:
    return await FlockService.get_flock(db, flock_id)


@router.put(
    "/{flock_id}",
    response_model=FlockResponse,
    summary="Update a flock",
)
async def update_flock(
    flock_id: int,
    request: FlockUpdate,
    current_user: Users = Depends(manage_flock),
    db: AsyncSession = Depends(get_db),
) -> FlockResponse:
    return await FlockService.update_flock(db, flock_id, request)


@router.delete(
    "/{flock_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a flock (admin only)",
)
async def delete_flock(
    flock_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await FlockService.delete_flock(db, flock_id)
