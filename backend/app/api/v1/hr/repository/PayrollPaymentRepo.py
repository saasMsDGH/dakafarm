from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.api.v1.hr.models.payroll_payment import PayrollPayment

class PayrollPaymentRepo:
    @staticmethod
    async def create(db: AsyncSession, payment: PayrollPayment) -> PayrollPayment:
        db.add(payment)
        # Service handles commit
        return payment

    @staticmethod
    async def list_payments_for_payroll(db: AsyncSession, payroll_id: int) -> List[PayrollPayment]:
        stmt = select(PayrollPayment).where(PayrollPayment.payroll_id == payroll_id).order_by(PayrollPayment.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
