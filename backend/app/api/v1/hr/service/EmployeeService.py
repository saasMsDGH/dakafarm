import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.repository.EmployeeRepo import EmployeeRepo
from app.api.v1.hr.schemas.EmployeeSchema import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class EmployeeService:
    @staticmethod
    def _generate_employee_code() -> str:
        # Generates a unique, short code for the employee, e.g. EMP-A1B2C3
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"EMP-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: EmployeeCreate, current_user_id: int) -> Employee:
        employee_code = EmployeeService._generate_employee_code()
        
        new_employee = Employee(
            employee_code=employee_code,
            first_name=request.first_name,
            last_name=request.last_name,
            position=request.position,
            phone=request.phone,
            employment_date=request.employment_date,
            status=request.status,
            created_by=current_user_id,
        )
        return await EmployeeRepo.create(db, new_employee)

    @staticmethod
    async def get_employee(db: AsyncSession, employee_id: int) -> Employee:
        employee = await EmployeeRepo.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )
        return employee

    @staticmethod
    async def list_employees(db: AsyncSession, params: PaginationParams) -> EmployeeListResponse:
        employees, total = await EmployeeRepo.list_employees(db, params)
        return EmployeeListResponse(
            items=employees,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, employee_id: int, request: EmployeeUpdate) -> Employee:
        employee = await EmployeeRepo.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await EmployeeRepo.update(db, employee, update_data)

    @staticmethod
    async def delete(db: AsyncSession, employee_id: int) -> None:
        employee = await EmployeeRepo.get_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )
        await EmployeeRepo.delete(db, employee)
