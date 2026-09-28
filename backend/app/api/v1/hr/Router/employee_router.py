from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.hr.schemas.EmployeeSchema import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.api.v1.hr.service.EmployeeService import EmployeeService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

hr_manager = RoleChecker(["admin", "hr_manager"])
hr_officer = RoleChecker(["admin", "hr_manager", "hr_officer"])

router = APIRouter(
    prefix="/employees",
    tags=["HR Employees"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee"
)
async def create_employee(
    request: EmployeeCreate,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    return await EmployeeService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=EmployeeListResponse,
    summary="List employees"
)
async def list_employees(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(hr_officer),
    db: AsyncSession = Depends(get_db),
) -> EmployeeListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await EmployeeService.list_employees(db, params)

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get an employee by ID"
)
async def get_employee(
    employee_id: int,
    current_user: Users = Depends(hr_officer),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    return await EmployeeService.get_employee(db, employee_id)

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update an employee"
)
async def update_employee(
    employee_id: int,
    request: EmployeeUpdate,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    return await EmployeeService.update(db, employee_id, request)

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an employee"
)
async def delete_employee(
    employee_id: int,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await EmployeeService.delete(db, employee_id)
