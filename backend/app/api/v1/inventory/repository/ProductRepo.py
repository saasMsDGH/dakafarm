from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.inventory.models.product import Product
from app.shared.pagination import PaginationParams

class ProductRepo:
    @staticmethod
    async def create(db: AsyncSession, product: Product) -> Product:
        try:
            db.add(product)
            await db.commit()
            await db.refresh(product)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this name already exists or category is invalid.",
            )
        return product

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: int) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    @staticmethod
    async def get_by_name(db: AsyncSession, product_name: str) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.name == product_name))
        return result.scalar_one_or_none()


    @staticmethod
    async def list_products(db: AsyncSession, params: PaginationParams, category_id: Optional[int] = None) -> Tuple[List[Product], int]:
        query = select(Product)

        if category_id:
            query = query.where(Product.category_id == category_id)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Product, params.sort_by, Product.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        products = list(result.scalars().all())

        return products, total

    @staticmethod
    async def update(db: AsyncSession, product: Product, data: dict) -> Product:
        for field, value in data.items():
            if value is not None:
                setattr(product, field, value)
        try:
            await db.commit()
            await db.refresh(product)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this name already exists or category is invalid.",
            )
        return product

    @staticmethod
    async def delete(db: AsyncSession, product: Product) -> None:
        try:
            await db.delete(product)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete product because it is referenced by stock transactions.",
            )
