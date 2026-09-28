from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.hr.schemas.PayrollSchema import (
    PayrollCreate,
    PayrollListResponse,
    PayrollResponse,
    PayrollUpdate,
)
from app.api.v1.hr.schemas.PayrollPaymentSchema import PayrollPaymentCreate, PayrollPaymentResponse
from app.api.v1.hr.service.PayrollService import PayrollService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

hr_manager = RoleChecker(["admin", "hr_manager"])
hr_officer = RoleChecker(["admin", "hr_manager", "hr_officer"])

router = APIRouter(
    prefix="/payrolls",
    tags=["HR Payroll"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=PayrollResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payroll record"
)
async def create_payroll(
    request: PayrollCreate,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> PayrollResponse:
    return await PayrollService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=PayrollListResponse,
    summary="List payroll records"
)
async def list_payrolls(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(hr_officer),
    db: AsyncSession = Depends(get_db),
) -> PayrollListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await PayrollService.list_payrolls(db, params)

@router.get(
    "/{payroll_id}",
    response_model=PayrollResponse,
    summary="Get a payroll record by ID"
)
async def get_payroll(
    payroll_id: int,
    current_user: Users = Depends(hr_officer),
    db: AsyncSession = Depends(get_db),
) -> PayrollResponse:
    return await PayrollService.get_payroll(db, payroll_id)

@router.put(
    "/{payroll_id}",
    response_model=PayrollResponse,
    summary="Update a payroll record"
)
async def update_payroll(
    payroll_id: int,
    request: PayrollUpdate,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> PayrollResponse:
    return await PayrollService.update(db, payroll_id, request)

@router.delete(
    "/{payroll_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a payroll record"
)
async def delete_payroll(
    payroll_id: int,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await PayrollService.delete(db, payroll_id)

@router.post(
    "/{payroll_id}/payments/",
    response_model=PayrollPaymentResponse,
    summary="Add a payment to a payroll record"
)
async def add_payment(
    payroll_id: int,
    request: PayrollPaymentCreate,
    current_user: Users = Depends(hr_manager),
    db: AsyncSession = Depends(get_db),
) -> PayrollPaymentResponse:
    return await PayrollService.add_payment(db, payroll_id, request, current_user.id)

@router.get(
    "/{payroll_id}/payments/",
    response_model=list[PayrollPaymentResponse],
    summary="List payments for a payroll record"
)
async def get_payments(
    payroll_id: int,
    current_user: Users = Depends(hr_officer),
    db: AsyncSession = Depends(get_db),
) -> list[PayrollPaymentResponse]:
    return await PayrollService.get_payments_for_payroll(db, payroll_id)
