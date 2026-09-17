from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.pos.models.customer import Customer
from app.shared.pagination import PaginationParams

class CustomerRepo:
    @staticmethod
    async def create(db: AsyncSession, customer: Customer) -> Customer:
        try:
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this code already exists."
            )
        return customer

    @staticmethod
    async def get_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_customers(db: AsyncSession, params: PaginationParams) -> Tuple[List[Customer], int]:
        query = select(Customer)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                    Customer.phone.ilike(search_term),
                    Customer.email.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Customer, params.sort_by, Customer.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        customers = list(result.scalars().all())

        return customers, total

    @staticmethod
    async def update(db: AsyncSession, customer: Customer, data: dict) -> Customer:
        for field, value in data.items():
            if value is not None:
                setattr(customer, field, value)
        try:
            await db.commit()
            await db.refresh(customer)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating customer."
            )
        return customer

    @staticmethod
    async def delete(db: AsyncSession, customer: Customer) -> None:
        try:
            await db.delete(customer)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete customer because they are referenced by existing transactions (e.g. Sales)."
            )
