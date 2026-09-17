from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.schemas.ProductSchema import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.api.v1.inventory.service.ProductService import ProductService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

manage_inventory = RoleChecker(["admin", "inventory_admin"])
admin = RoleChecker(["admin"])

router = APIRouter(
    prefix="/products",
    tags=["Inventory Products"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(
    request: ProductCreate,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    return await ProductService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=ProductListResponse,
    summary="List products",
)
async def list_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    category_id: Optional[int] = Query(default=None, description="Filter by category"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await ProductService.list_products(db, params, category_id)

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get a product",
)
async def get_product(
    product_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    return await ProductService.get_product(db, product_id)

@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
)
async def update_product(
    product_id: int,
    request: ProductUpdate,
    current_user: Users = Depends(admin),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    return await ProductService.update(db, product_id, request, current_user.id)

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
async def delete_product(
    product_id: int,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ProductService.delete(db, product_id)

