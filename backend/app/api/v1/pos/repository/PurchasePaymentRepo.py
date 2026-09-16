from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.pos.models.purchase_payment import PurchasePayment

class PurchasePaymentRepo:
    @staticmethod
    async def create(db: AsyncSession, payment: PurchasePayment) -> PurchasePayment:
        db.add(payment)
        await db.flush()
        return payment

    @staticmethod
    async def list_payments_for_purchase(db: AsyncSession, purchase_id: int) -> List[PurchasePayment]:
        result = await db.execute(
            select(PurchasePayment)
            .where(PurchasePayment.purchase_id == purchase_id)
            .order_by(PurchasePayment.payment_date.desc())
        )
        return list(result.scalars().all())
