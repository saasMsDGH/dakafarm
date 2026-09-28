from typing import Optional, Tuple, List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.shared.pagination import PaginationParams

class StockMovementRepo:
    @staticmethod
    async def create(db: AsyncSession, movement: StockMovement) -> StockMovement:
        db.add(movement)
        # Flush to get the ID without committing so Service can commit safely with Product
        await db.flush()
        return movement

    @staticmethod
    async def get_by_id(db: AsyncSession, movement_id: int) -> Optional[StockMovement]:
        result = await db.execute(select(StockMovement).where(StockMovement.id == movement_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_movements(
        db: AsyncSession, 
        params: PaginationParams, 
        product_id: Optional[int] = None,
        movement_type: Optional[str] = None
    ) -> Tuple[List[StockMovement], int]:
        query = select(StockMovement)

        if product_id:
            query = query.where(StockMovement.product_id == product_id)
        if movement_type:
            query = query.where(StockMovement.movement_type == movement_type)

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(StockMovement, params.sort_by, StockMovement.movement_date)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        movements = list(result.scalars().all())

        return movements, total
