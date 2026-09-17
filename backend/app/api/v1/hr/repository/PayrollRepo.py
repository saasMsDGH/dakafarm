from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.hr.models.employee import Employee
from app.shared.pagination import PaginationParams

class PayrollRepo:
    @staticmethod
    async def create(db: AsyncSession, payroll: Payroll) -> Payroll:
        try:
            db.add(payroll)
            await db.commit()
            await db.refresh(payroll)
            # Load relationships
            result = await db.execute(select(Payroll).options(selectinload(Payroll.employee), selectinload(Payroll.user)).where(Payroll.id == payroll.id))
            return result.scalar_one()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Integrity error creating payroll record. Ensure employee exists."
            )

    @staticmethod
    async def get_by_id(db: AsyncSession, payroll_id: int) -> Optional[Payroll]:
        result = await db.execute(
            select(Payroll)
            .options(selectinload(Payroll.employee), selectinload(Payroll.user))
            .where(Payroll.id == payroll_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_payrolls(db: AsyncSession, params: PaginationParams) -> Tuple[List[Payroll], int]:
        query = select(Payroll).join(Employee).options(selectinload(Payroll.employee), selectinload(Payroll.user))

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Payroll.pay_period.ilike(search_term),
                    Payroll.payment_status.ilike(search_term),
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term)
                )
            )

        # For count, we can just use the base query without options
        count_query = select(func.count()).select_from(Payroll).join(Employee)
        if params.search:
            search_term = f"%{params.search}%"
            count_query = count_query.where(
                or_(
                    Payroll.pay_period.ilike(search_term),
                    Payroll.payment_status.ilike(search_term),
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term)
                )
            )
            
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Note: If sorting by a column in Payroll
        sort_column = getattr(Payroll, params.sort_by, Payroll.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        payrolls = list(result.scalars().all())

        return payrolls, total

    @staticmethod
    async def update(db: AsyncSession, payroll: Payroll, data: dict) -> Payroll:
        for field, value in data.items():
            if value is not None:
                setattr(payroll, field, value)
        try:
            await db.commit()
            await db.refresh(payroll)
            # Re-load employee
            result = await db.execute(select(Payroll).options(selectinload(Payroll.employee), selectinload(Payroll.user)).where(Payroll.id == payroll.id))
            return result.scalar_one()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating payroll."
            )

    @staticmethod
    async def delete(db: AsyncSession, payroll: Payroll) -> None:
        try:
            await db.delete(payroll)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete payroll record."
            )
