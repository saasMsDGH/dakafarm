import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.hr.models.payroll_payment import PayrollPayment
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.hr.repository.PayrollRepo import PayrollRepo
from app.api.v1.hr.repository.PayrollPaymentRepo import PayrollPaymentRepo
from app.api.v1.finance.repository.AccountRepo import AccountRepo
from app.api.v1.hr.schemas.PayrollSchema import (
    PayrollCreate,
    PayrollListResponse,
    PayrollUpdate,
)
from app.api.v1.hr.schemas.PayrollPaymentSchema import PayrollPaymentCreate
from app.shared.pagination import PaginationParams, compute_pages

class PayrollService:
    @staticmethod
    def _generate_payment_reference() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"PAYROLLPAY-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: PayrollCreate, current_user_id: int) -> Payroll:
        net_salary = request.basic_salary + request.allowances - request.deductions
        
        if request.amount_paid > net_salary:
            raise HTTPException(status_code=400, detail="Amount paid cannot exceed net salary.")

        if request.amount_paid > 0:
            if not request.account_id:
                raise HTTPException(status_code=400, detail="account_id is required if amount_paid > 0")
            if not request.payment_method:
                raise HTTPException(status_code=400, detail="payment_method is required if amount_paid > 0")
            
            # Verify account exists
            account = await AccountRepo.get_by_id(db, request.account_id)
            if not account:
                raise HTTPException(status_code=404, detail="Financial account not found.")

        # Determine payment status
        if request.amount_paid == net_salary:
            payment_status = "PAID"
        elif request.amount_paid > 0:
            payment_status = "PARTIAL"
        else:
            payment_status = "UNPAID"
            
        new_payroll = Payroll(
            employee_id=request.employee_id,
            pay_period=request.pay_period,
            basic_salary=request.basic_salary,
            allowances=request.allowances,
            deductions=request.deductions,
            net_salary=net_salary,
            amount_paid=request.amount_paid,
            payment_date=request.payment_date,
            payment_status=payment_status,
            created_by=current_user_id,
        )
        created_payroll = await PayrollRepo.create(db, new_payroll, commit=False)

        if request.amount_paid > 0:
            # 1. Create PayrollPayment
            payment_ref = PayrollService._generate_payment_reference()
            payroll_payment = PayrollPayment(
                payroll_id=created_payroll.id,
                account_id=request.account_id,
                payment_reference=payment_ref,
                amount=request.amount_paid,
                payment_method=request.payment_method,
                paid_by=current_user_id
            )
            await PayrollPaymentRepo.create(db, payroll_payment)

            # 2. Create FinancialTransaction
            fin_txn = FinancialTransaction(
                account_id=request.account_id,
                transaction_type="PAYROLL",
                direction="OUT",
                amount=request.amount_paid,
                description=f"Payroll Payment for {request.pay_period}",
                reference_number=payment_ref,
                created_by=current_user_id
            )
            db.add(fin_txn)

        try:
            payroll_id = created_payroll.id
            await db.commit()
            return await PayrollRepo.get_by_id(db, payroll_id)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

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
            
            # Recalculate status based on new net_salary
            net = update_data["net_salary"]
            if payroll.amount_paid >= net:
                update_data["payment_status"] = "PAID"
            elif payroll.amount_paid > 0:
                update_data["payment_status"] = "PARTIAL"
            else:
                update_data["payment_status"] = "UNPAID"

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

    @staticmethod
    async def add_payment(db: AsyncSession, payroll_id: int, request: PayrollPaymentCreate, current_user_id: int) -> PayrollPayment:
        payroll = await PayrollRepo.get_by_id(db, payroll_id)
        if not payroll:
            raise HTTPException(status_code=404, detail="Payroll not found.")

        if payroll.payment_status == "PAID":
            raise HTTPException(status_code=400, detail="Payroll is already fully paid.")

        remaining = payroll.net_salary - payroll.amount_paid
        if request.amount > remaining:
            raise HTTPException(status_code=400, detail=f"Payment amount exceeds remaining balance of {remaining}.")

        # Verify account
        account = await AccountRepo.get_by_id(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Financial account not found.")

        payment_ref = PayrollService._generate_payment_reference()

        # 1. Create PayrollPayment
        payment = PayrollPayment(
            payroll_id=payroll.id,
            account_id=request.account_id,
            payment_reference=payment_ref,
            amount=request.amount,
            payment_method=request.payment_method,
            paid_by=current_user_id
        )
        await PayrollPaymentRepo.create(db, payment)

        # 2. Update Payroll
        payroll.amount_paid += request.amount
        if payroll.amount_paid >= payroll.net_salary:
            payroll.payment_status = "PAID"
        else:
            payroll.payment_status = "PARTIAL"

        # 3. Create FinancialTransaction
        fin_txn = FinancialTransaction(
            account_id=request.account_id,
            transaction_type="PAYROLL",
            direction="OUT",
            amount=request.amount,
            description=f"Payroll Payment for {payroll.pay_period}",
            reference_number=payment_ref,
            created_by=current_user_id
        )
        db.add(fin_txn)

        try:
            await db.flush()
            payment_id = payment.id
            await db.commit()
            res = await db.execute(select(PayrollPayment).where(PayrollPayment.id == payment_id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

    @staticmethod
    async def get_payments_for_payroll(db: AsyncSession, payroll_id: int) -> list[PayrollPayment]:
        return await PayrollPaymentRepo.list_payments_for_payroll(db, payroll_id)
