from typing import Optional, Tuple, List
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.api.v1.pos.models.purchase import Purchase, PurchaseItem
from app.shared.pagination import PaginationParams

class PurchaseRepo:
    @staticmethod
    async def create(db: AsyncSession, purchase: Purchase) -> Purchase:
        db.add(purchase)
        await db.flush()  # flush to get the ID but not commit yet
        return purchase

    @staticmethod
    async def create_item(db: AsyncSession, item: PurchaseItem) -> PurchaseItem:
        db.add(item)
        await db.flush()
        return item

    @staticmethod
    async def get_by_id(db: AsyncSession, purchase_id: int) -> Optional[Purchase]:
        result = await db.execute(
            select(Purchase)
            .options(selectinload(Purchase.items), selectinload(Purchase.payments))
            .where(Purchase.id == purchase_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_purchases(db: AsyncSession, params: PaginationParams, supplier_id: Optional[int] = None) -> Tuple[List[Purchase], int]:
        query = select(Purchase).options(selectinload(Purchase.items), selectinload(Purchase.payments))

        if supplier_id:
            query = query.where(Purchase.supplier_id == supplier_id)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Purchase.purchase_number.ilike(search_term),
                    Purchase.payment_status.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Purchase, params.sort_by, Purchase.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        purchases = list(result.scalars().all())

        return purchases, total

    @staticmethod
    async def get_supplier_outstanding_balance(db: AsyncSession, supplier_id: int) -> float:
        """Sum of (total_amount - amount_paid) for all purchases from this supplier."""
        query = select(func.sum(Purchase.total_amount - Purchase.amount_paid)).where(Purchase.supplier_id == supplier_id)
        result = await db.execute(query)
        balance = result.scalar()
        return float(balance) if balance else 0.0
