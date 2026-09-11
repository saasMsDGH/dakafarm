from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.schemas.InventorySchema import InventoryListResponse, InventoryResponse
from app.api.v1.inventory.service.InventoryService import InventoryService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

manage_inventory = RoleChecker(["admin", "inventory_admin"])

router = APIRouter(
    prefix="/stock",
    tags=["Inventory Stock Status"],
    redirect_slashes=False,
)

@router.get(
    "/",
    response_model=InventoryListResponse,
    summary="List current inventory stock positions",
)
async def list_inventory(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    category_id: Optional[int] = Query(default=None, description="Filter by category"),
    status_filter: Optional[str] = Query(default=None, description="Filter by status (e.g., 'Low Stock')"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InventoryListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await InventoryService.list_inventory(db, params, category_id, status_filter)

@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
    summary="Get current stock position for a single product",
)
async def get_inventory_status(
    product_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InventoryResponse:
    return await InventoryService.get_inventory_status(db, product_id)
