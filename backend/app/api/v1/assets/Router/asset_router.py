from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.assets.schemas.AssetSchema import (
    AssetCreate,
    AssetListResponse,
    AssetResponse,
    AssetUpdate,
)
from app.api.v1.assets.service.AssetService import AssetService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

# Define roles allowed for Assets
asset_manager = RoleChecker(["admin", "farm_manager", "asset_manager"])
asset_viewer = RoleChecker(["admin", "farm_manager", "asset_manager", "inventory_admin"])

router = APIRouter(
    prefix="/list",
    tags=["Assets"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new asset"
)
async def create_asset(
    request: AssetCreate,
    current_user: Users = Depends(asset_manager),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    return await AssetService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=AssetListResponse,
    summary="List assets"
)
async def list_assets(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(asset_viewer),
    db: AsyncSession = Depends(get_db),
) -> AssetListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await AssetService.list_assets(db, params)

@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Get an asset by ID"
)
async def get_asset(
    asset_id: int,
    current_user: Users = Depends(asset_viewer),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    return await AssetService.get_asset(db, asset_id)

@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="Update an asset"
)
async def update_asset(
    asset_id: int,
    request: AssetUpdate,
    current_user: Users = Depends(asset_manager),
    db: AsyncSession = Depends(get_db),
) -> AssetResponse:
    return await AssetService.update(db, asset_id, request)

@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an asset"
)
async def delete_asset(
    asset_id: int,
    current_user: Users = Depends(asset_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await AssetService.delete(db, asset_id)
