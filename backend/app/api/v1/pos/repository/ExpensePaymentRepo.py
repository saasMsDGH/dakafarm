from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.api.v1.pos.models.expense_payment import ExpensePayment

class ExpensePaymentRepo:
    @staticmethod
    async def create(db: AsyncSession, payment: ExpensePayment) -> ExpensePayment:
        db.add(payment)
        # Note: We rely on the Service layer to commit this transaction
        return payment

    @staticmethod
    async def get_by_id(db: AsyncSession, payment_id: int) -> ExpensePayment:
        result = await db.execute(select(ExpensePayment).where(ExpensePayment.id == payment_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_payments_for_expense(db: AsyncSession, expense_id: int) -> list[ExpensePayment]:
        result = await db.execute(
            select(ExpensePayment)
            .where(ExpensePayment.expense_id == expense_id)
            .order_by(ExpensePayment.created_at.desc())
        )
        return list(result.scalars().all())
