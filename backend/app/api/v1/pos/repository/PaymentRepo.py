from typing import Optional, Tuple, List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.pos.models.payment import Payment
from app.shared.pagination import PaginationParams

class PaymentRepo:
    @staticmethod
    async def create(db: AsyncSession, payment: Payment) -> Payment:
        db.add(payment)
        await db.flush()
        return payment

    @staticmethod
    async def list_payments_for_sale(db: AsyncSession, sale_id: int) -> List[Payment]:
        result = await db.execute(select(Payment).where(Payment.sale_id == sale_id).order_by(Payment.payment_date.desc()))
        return list(result.scalars().all())
