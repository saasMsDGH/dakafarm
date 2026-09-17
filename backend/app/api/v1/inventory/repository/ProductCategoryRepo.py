from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.inventory.models.product_category import ProductCategory
from app.shared.pagination import PaginationParams

class ProductCategoryRepo:
    @staticmethod
    async def create(db: AsyncSession, category: ProductCategory) -> ProductCategory:
        try:
            db.add(category)
            await db.commit()
            await db.refresh(category)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists.",
            )
        return category

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Optional[ProductCategory]:
        result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[ProductCategory]:
        result = await db.execute(select(ProductCategory).where(ProductCategory.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories(db: AsyncSession, params: PaginationParams) -> Tuple[List[ProductCategory], int]:
        query = select(ProductCategory)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    ProductCategory.name.ilike(search_term),
                    ProductCategory.description.ilike(search_term),
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(ProductCategory, params.sort_by, ProductCategory.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        categories = list(result.scalars().all())

        return categories, total

    @staticmethod
    async def update(db: AsyncSession, category: ProductCategory, data: dict) -> ProductCategory:
        for field, value in data.items():
            if value is not None:
                setattr(category, field, value)
        try:
            await db.commit()
            await db.refresh(category)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists.",
            )
        return category

    @staticmethod
    async def delete(db: AsyncSession, category: ProductCategory) -> None:
        await db.delete(category)
        await db.commit()
