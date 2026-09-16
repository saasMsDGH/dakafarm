from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.pos.models.expense import Expense
from app.shared.pagination import PaginationParams

class ExpenseRepo:
    @staticmethod
    async def create(db: AsyncSession, expense: Expense) -> Expense:
        try:
            db.add(expense)
            await db.commit()
            await db.refresh(expense)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An expense with this number already exists."
            )
        return expense

    @staticmethod
    async def get_by_id(db: AsyncSession, expense_id: int) -> Optional[Expense]:
        result = await db.execute(select(Expense).where(Expense.id == expense_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_expenses(db: AsyncSession, params: PaginationParams, category: Optional[str] = None) -> Tuple[List[Expense], int]:
        query = select(Expense)

        if category:
            query = query.where(Expense.category.ilike(f"%{category}%"))

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Expense.expense_number.ilike(search_term),
                    Expense.category.ilike(search_term),
                    Expense.description.ilike(search_term),
                    Expense.payment_method.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Expense, params.sort_by, Expense.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        expenses = list(result.scalars().all())

        return expenses, total

    @staticmethod
    async def update(db: AsyncSession, expense: Expense, data: dict) -> Expense:
        for field, value in data.items():
            if value is not None:
                setattr(expense, field, value)
        try:
            await db.commit()
            await db.refresh(expense)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating expense."
            )
        return expense

    @staticmethod
    async def delete(db: AsyncSession, expense: Expense) -> None:
        await db.delete(expense)
        await db.commit()
