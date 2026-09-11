from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.models.product_category import ProductCategory
from app.api.v1.inventory.repository.ProductCategoryRepo import ProductCategoryRepo
from app.api.v1.inventory.schemas.ProductCategorySchema import (
    ProductCategoryCreate,
    ProductCategoryListResponse,
    ProductCategoryUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class ProductCategoryService:
    @staticmethod
    async def create(db: AsyncSession, request: ProductCategoryCreate, current_user_id: int) -> ProductCategory:
        new_category = ProductCategory(
            name=request.name,
            description=request.description,
            is_active=request.is_active,
            created_by=current_user_id,
        )
        return await ProductCategoryRepo.create(db, new_category)

    @staticmethod
    async def get_category(db: AsyncSession, category_id: int) -> ProductCategory:
        category = await ProductCategoryRepo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductCategory with id {category_id} not found.",
            )
        return category

    @staticmethod
    async def list_categories(db: AsyncSession, params: PaginationParams) -> ProductCategoryListResponse:
        categories, total = await ProductCategoryRepo.list_categories(db, params)
        return ProductCategoryListResponse(
            items=categories,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, category_id: int, request: ProductCategoryUpdate) -> ProductCategory:
        category = await ProductCategoryRepo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductCategory with id {category_id} not found.",
            )
        update_data = request.model_dump(exclude_unset=True)
        return await ProductCategoryRepo.update(db, category, update_data)

    @staticmethod
    async def delete(db: AsyncSession, category_id: int) -> None:
        category = await ProductCategoryRepo.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductCategory with id {category_id} not found.",
            )
        # Assuming no dependencies constraint check needed for now, can be added later
        await ProductCategoryRepo.delete(db, category)

        return {"message": "category deleted successfuly"}
