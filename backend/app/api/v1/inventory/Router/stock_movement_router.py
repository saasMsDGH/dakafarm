from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.schemas.StockMovementSchema import (
    StockMovementCreate,
    StockMovementListResponse,
    StockMovementResponse,
)
from app.api.v1.inventory.service.StockMovementService import StockMovementService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

manage_inventory = RoleChecker(["admin", "inventory_admin"])

router = APIRouter(
    prefix="/movements",
    tags=["Inventory Stock Movements"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a stock movement",
)
async def create_movement(
    request: StockMovementCreate,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> StockMovementResponse:
    """
    Creates a stock movement and automatically updates the associated product's current stock.
    IN adds stock, OUT subtracts stock, ADJUSTMENT adds the provided quantity (which can be negative).
    """
    return await StockMovementService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=StockMovementListResponse,
    summary="List stock movements",
)
async def list_movements(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="movement_date"),
    order: str = Query(default="desc"),
    product_id: Optional[int] = Query(default=None, description="Filter by product"),
    movement_type: Optional[str] = Query(default=None, description="Filter by type (IN, OUT, ADJUSTMENT)"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockMovementListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await StockMovementService.list_movements(db, params, product_id, movement_type)

@router.get(
    "/{movement_id}",
    response_model=StockMovementResponse,
    summary="Get a stock movement",
)
async def get_movement(
    movement_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockMovementResponse:
    return await StockMovementService.get_movement(db, movement_id)
