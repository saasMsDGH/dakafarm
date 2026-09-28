from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.schemas.ProductCategorySchema import (
    ProductCategoryCreate,
    ProductCategoryListResponse,
    ProductCategoryResponse,
    ProductCategoryUpdate,
)
from app.api.v1.inventory.service.ProductCategoryService import ProductCategoryService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

manage_inventory = RoleChecker(["admin", "inventory_admin"])

router = APIRouter(
    prefix="/product-categories",
    tags=["Inventory Product Categories"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product category",
)
async def create_category(
    request: ProductCategoryCreate,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> ProductCategoryResponse:
    return await ProductCategoryService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=ProductCategoryListResponse,
    summary="List product categories",
)
async def list_categories(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductCategoryListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await ProductCategoryService.list_categories(db, params)

@router.get(
    "/{category_id}",
    response_model=ProductCategoryResponse,
    summary="Get a product category",
)
async def get_category(
    category_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductCategoryResponse:
    return await ProductCategoryService.get_category(db, category_id)

@router.put(
    "/{category_id}",
    response_model=ProductCategoryResponse,
    summary="Update a product category",
)
async def update_category(
    category_id: int,
    request: ProductCategoryUpdate,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> ProductCategoryResponse:
    return await ProductCategoryService.update(db, category_id, request)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product category",
)
async def delete_category(
    category_id: int,
    current_user: Users = Depends(manage_inventory),
    db: AsyncSession = Depends(get_db),
) -> None:
    await ProductCategoryService.delete(db, category_id)
