from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.hr.repository.PayrollRepo import PayrollRepo
from app.api.v1.hr.schemas.PayrollSchema import (
    PayrollCreate,
    PayrollListResponse,
    PayrollUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages
from decimal import Decimal

class PayrollService:
    @staticmethod
    async def create(db: AsyncSession, request: PayrollCreate, current_user_id: int) -> Payroll:
        net_salary = request.basic_salary + request.allowances - request.deductions
        
        new_payroll = Payroll(
            employee_id=request.employee_id,
            pay_period=request.pay_period,
            basic_salary=request.basic_salary,
            allowances=request.allowances,
            deductions=request.deductions,
            net_salary=net_salary,
            payment_date=request.payment_date,
            payment_status=request.payment_status,
            created_by=current_user_id,
        )
        return await PayrollRepo.create(db, new_payroll)

    @staticmethod
    async def get_payroll(db: AsyncSession, payroll_id: int) -> Payroll:
        payroll = await PayrollRepo.get_by_id(db, payroll_id)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payroll with id {payroll_id} not found."
            )
        return payroll

    @staticmethod
    async def list_payrolls(db: AsyncSession, params: PaginationParams) -> PayrollListResponse:
        payrolls, total = await PayrollRepo.list_payrolls(db, params)
        return PayrollListResponse(
            items=payrolls,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, payroll_id: int, request: PayrollUpdate) -> Payroll:
        payroll = await PayrollRepo.get_by_id(db, payroll_id)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payroll with id {payroll_id} not found."
            )
            
        update_data = request.model_dump(exclude_unset=True)
        
        # If any financial field is updated, we need to recalculate net_salary
        if any(k in update_data for k in ["basic_salary", "allowances", "deductions"]):
            basic = update_data.get("basic_salary", payroll.basic_salary) or Decimal('0.00')
            allowances = update_data.get("allowances", payroll.allowances) or Decimal('0.00')
            deductions = update_data.get("deductions", payroll.deductions) or Decimal('0.00')
            update_data["net_salary"] = basic + allowances - deductions

        return await PayrollRepo.update(db, payroll, update_data)

    @staticmethod
    async def delete(db: AsyncSession, payroll_id: int) -> None:
        payroll = await PayrollRepo.get_by_id(db, payroll_id)
        if not payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payroll with id {payroll_id} not found."
            )
        await PayrollRepo.delete(db, payroll)
