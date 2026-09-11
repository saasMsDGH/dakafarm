"""
FeedRecord service — business logic.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.repository.FeedRecordRepo import FeedRecordRepo
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.farm.schemas.FeedRecordSchema import (
    FeedRecordCreate,
    FeedRecordListResponse,
    FeedRecordUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class FeedRecordService:
    """Business logic for FeedRecord."""

    @staticmethod
    async def create(
        db: AsyncSession,
        request: FeedRecordCreate,
        current_user_id: int,
    ) -> FeedRecord:
        """Create a new feed record."""
        # 1. Validate Flock exists
        flock = await FlockRepo.get_by_id(db, request.flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {request.flock_id} not found.",
            )

        product = await ProductRepo.get_by_id(db, request.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product with that id not found"
            )

        
   
        closing  = request.opening_quantity - request.quantity_used

        if request.quantity_used > request.opening_quantity:
            raise HTTPException(
                status_code=400,
                detail="the quantity used value can't be bigger than opening quantity"
            )
        total_cost = request.quantity_used * request.cost_per_unit

        new_record = FeedRecord(
            flock_id=request.flock_id,
            product_id=request.product_id,
            record_date=request.record_date,
            opening_quantity=request.opening_quantity,
            quantity_used=request.quantity_used,
            closing_quantity=closing,
            cost_per_unit=request.cost_per_unit,
            total_cost=total_cost,
            recorded_by=current_user_id,
        )
        return await FeedRecordRepo.create(db, new_record)

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int) -> FeedRecord:
        """Return a single feed record."""
        record = await FeedRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FeedRecord with id {record_id} not found.",
            )
        return record

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> FeedRecordListResponse:
        """List paginated feed records."""
        records, total = await FeedRecordRepo.list_records(db, params)
        return FeedRecordListResponse(
            items=records,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(
        db: AsyncSession,
        record_id: int,
        request: FeedRecordUpdate,
    ) -> FeedRecord:
        """Update a feed record."""
        record = await FeedRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FeedRecord with id {record_id} not found.",
            )
            
        # Validate new flock_id if it's changing
        if request.flock_id is not None and request.flock_id != record.flock_id:
            flock = await FlockRepo.get_by_id(db, request.flock_id)
            if not flock:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Flock with id {request.flock_id} not found.",
                )

        update_data = request.model_dump(exclude_unset=True)
        
        # Auto-recalculate total_cost if quantity_used or cost_per_unit changes
        # But only if total_cost is not explicitly being overridden
        if "total_cost" not in update_data:
            new_qty = update_data.get("quantity_used", record.quantity_used)
            new_cost = update_data.get("cost_per_unit", record.cost_per_unit)
            
            if new_qty is not None and new_cost is not None:
                update_data["total_cost"] = new_qty * new_cost

        return await FeedRecordRepo.update(db, record, update_data)

    @staticmethod
    async def delete(db: AsyncSession, record_id: int) -> None:
        """Delete a feed record."""
        record = await FeedRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FeedRecord with id {record_id} not found.",
            )
        await FeedRecordRepo.delete(db, record)
