"""
House router — HTTP endpoints for the House resource.

Route summary:
  POST   /api/v1/farm/houses          Create house     (admin, Farm Manager)
  GET    /api/v1/farm/houses          List houses      (any authenticated user)
  GET    /api/v1/farm/houses/{id}     Get house        (any authenticated user)
  PUT    /api/v1/farm/houses/{id}     Update house     (admin, Farm Manager)
  DELETE /api/v1/farm/houses/{id}     Delete house     (admin only)

Routers are thin — they validate HTTP, inject dependencies, call services,
and return responses. No business logic lives here.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.schemas.HouseSchema import (
    HouseCreate,
    HouseListResponse,
    HouseResponse,
    HouseUpdate,
)
from app.api.v1.farm.service.HouseService import HouseService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# ── RBAC role checkers ─────────────────────────────────────────────────────────
manage_house = RoleChecker(["admin", "Farm Manager"])
admin_only = RoleChecker(["admin"])

# ── Router ─────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/houses",
    tags=["Houses"],
    redirect_slashes=False,
)


@router.post(
    "/",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new house",
)
async def create_house(
    request: HouseCreate,
    current_user: Users = Depends(manage_house),
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    return await HouseService.create_house(db, request, current_user.id)


@router.get(
    "/",
    response_model=HouseListResponse,
    summary="List all houses (paginated)",
)
async def list_houses(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search by name or location"),
    sort_by: str = Query(default="created_at", description="Column to sort by"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HouseListResponse:
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    return await HouseService.list_houses(db, params)


@router.get(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Get a single house by ID",
)
async def get_house(
    house_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    return await HouseService.get_house(db, house_id)


@router.put(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Update a house",
)
async def update_house(
    house_id: int,
    request: HouseUpdate,
    current_user: Users = Depends(manage_house),
    db: AsyncSession = Depends(get_db),
) -> HouseResponse:
    return await HouseService.update_house(db, house_id, request)


@router.delete(
    "/{house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a house (admin only)",
)
async def delete_house(
    house_id: int,
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db),
) -> None:
    await HouseService.delete_house(db, house_id)
