from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.pos.models.supplier import Supplier
from app.shared.pagination import PaginationParams

class SupplierRepo:
    @staticmethod
    async def create(db: AsyncSession, supplier: Supplier) -> Supplier:
        try:
            db.add(supplier)
            await db.commit()
            await db.refresh(supplier)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A supplier with this code already exists."
            )
        return supplier

    @staticmethod
    async def get_by_id(db: AsyncSession, supplier_id: int) -> Optional[Supplier]:
        result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_suppliers(db: AsyncSession, params: PaginationParams) -> Tuple[List[Supplier], int]:
        query = select(Supplier)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.supplier_code.ilike(search_term),
                    Supplier.phone.ilike(search_term),
                    Supplier.email.ilike(search_term),
                    Supplier.contact_person.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Supplier, params.sort_by, Supplier.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        suppliers = list(result.scalars().all())

        return suppliers, total

    @staticmethod
    async def update(db: AsyncSession, supplier: Supplier, data: dict) -> Supplier:
        for field, value in data.items():
            if value is not None:
                setattr(supplier, field, value)
        try:
            await db.commit()
            await db.refresh(supplier)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating supplier."
            )
        return supplier

    @staticmethod
    async def delete(db: AsyncSession, supplier: Supplier) -> None:
        try:
            await db.delete(supplier)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete supplier because they are referenced by existing purchases."
            )
