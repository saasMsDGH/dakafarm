from typing import Optional, Tuple, List
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.api.v1.pos.models.sale import Sale, SaleItem
from app.shared.pagination import PaginationParams

class SaleRepo:
    @staticmethod
    async def create(db: AsyncSession, sale: Sale) -> Sale:
        db.add(sale)
        await db.flush() # flush to get the ID but not commit yet
        return sale

    @staticmethod
    async def create_item(db: AsyncSession, item: SaleItem) -> SaleItem:
        db.add(item)
        await db.flush()
        return item

    @staticmethod
    async def get_by_id(db: AsyncSession, sale_id: int) -> Optional[Sale]:
        result = await db.execute(
            select(Sale)
            .options(selectinload(Sale.items), selectinload(Sale.payments))
            .where(Sale.id == sale_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sales(db: AsyncSession, params: PaginationParams, customer_id: Optional[int] = None) -> Tuple[List[Sale], int]:
        query = select(Sale).options(selectinload(Sale.items), selectinload(Sale.payments))

        if customer_id:
            query = query.where(Sale.customer_id == customer_id)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Sale.invoice_number.ilike(search_term),
                    Sale.payment_status.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Sale, params.sort_by, Sale.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        sales = list(result.scalars().all())

        return sales, total

    @staticmethod
    async def get_outstanding_balance(db: AsyncSession, customer_id: int) -> float:
        # Sum of (total_amount - amount_paid) for all sales of this customer
        query = select(func.sum(Sale.total_amount - Sale.amount_paid)).where(Sale.customer_id == customer_id)
        result = await db.execute(query)
        balance = result.scalar()
        return float(balance) if balance else 0.0


