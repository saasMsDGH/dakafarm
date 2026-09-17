from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.hr.models.employee import Employee
from app.shared.pagination import PaginationParams

class EmployeeRepo:
    @staticmethod
    async def create(db: AsyncSession, employee: Employee) -> Employee:
        try:
            db.add(employee)
            await db.commit()
            await db.refresh(employee)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An employee with this code already exists."
            )
        return employee

    @staticmethod
    async def get_by_id(db: AsyncSession, employee_id: int) -> Optional[Employee]:
        result = await db.execute(select(Employee).where(Employee.id == employee_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_employees(db: AsyncSession, params: PaginationParams) -> Tuple[List[Employee], int]:
        query = select(Employee)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.employee_code.ilike(search_term),
                    Employee.position.ilike(search_term),
                    Employee.phone.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Employee, params.sort_by, Employee.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        employees = list(result.scalars().all())

        return employees, total

    @staticmethod
    async def update(db: AsyncSession, employee: Employee, data: dict) -> Employee:
        for field, value in data.items():
            if value is not None:
                setattr(employee, field, value)
        try:
            await db.commit()
            await db.refresh(employee)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating employee."
            )
        return employee

    @staticmethod
    async def delete(db: AsyncSession, employee: Employee) -> None:
        try:
            await db.delete(employee)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete employee because they are referenced by other records."
            )
