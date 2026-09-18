from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.api.v1.assets.models.asset_payment import AssetPayment

class AssetPaymentRepo:
    @staticmethod
    async def create(db: AsyncSession, payment: AssetPayment) -> AssetPayment:
        db.add(payment)
        return payment

    @staticmethod
    async def list_payments_for_asset(db: AsyncSession, asset_id: int) -> List[AssetPayment]:
        stmt = select(AssetPayment).where(AssetPayment.asset_id == asset_id).order_by(AssetPayment.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
