"""
FeedRecord service - business logic.
"""

from fastapi import HTTPException, status
from app.shared.transactions import atomic
from app.api.v1.campaigns.service import require_unassigned
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from datetime import datetime, time, timezone

from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.repository.FeedRecordRepo import FeedRecordRepo
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.inventory.schemas.StockMovementSchema import StockMovementCreate
from app.api.v1.inventory.service.StockMovementService import StockMovementService
from app.api.v1.farm.schemas.FeedRecordSchema import (
    FeedRecordCreate,
    FeedRecordListResponse,
    FeedRecordUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class FeedRecordService:
    """Business logic for FeedRecord."""

    @staticmethod
    @atomic
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

        # 2. Check Product Stock securely
        if not request.product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product_id is strictly required for feed records."
            )
            
        product = await ProductRepo.get_by_id(db, request.product_id, for_update=True)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product with that id not found"
            )

        # Ensure enough stock is available before proceeding
        if product.current_stock < request.quantity_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock! You tried to use {request.quantity_used}, but only {product.current_stock} is available."
            )

        # Automatically fill opening quantity from current inventory stock
        opening = product.current_stock
        closing = opening - request.quantity_used
        
        # 2. Auto-calculations
        actual_cost_per_unit = product.unit_price
        total_cost = request.quantity_used * actual_cost_per_unit

        # 3. Create the Farm Record
        new_record = FeedRecord(
            flock_id=request.flock_id,
            product_id=request.product_id,
            record_date=request.record_date,
            opening_quantity=opening,
            quantity_used=request.quantity_used,
            closing_quantity=closing,
            cost_per_unit=actual_cost_per_unit,
            total_cost=total_cost,
            recorded_by=current_user_id,
        )
        created_record = await FeedRecordRepo.create(db, new_record, commit=False)

        # 4. Automate the Inventory Movement
        movement_request = StockMovementCreate(
            product_id=request.product_id,
            movement_type="OUT",
            quantity=request.quantity_used,
            reference_type="FeedRecord",
            reference_id=created_record.id,
            movement_date=datetime.combine(request.record_date, time.min, timezone.utc)
        )
        await StockMovementService.create(db, movement_request, current_user_id, commit=False)
        
        await db.refresh(created_record)
        return created_record

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int) -> FeedRecord:
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
        records, total = await FeedRecordRepo.list_records(db, params)
        return FeedRecordListResponse(
            items=records,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    @atomic
    async def update(
        db: AsyncSession,
        record_id: int,
        request: FeedRecordUpdate,
        current_user_id: int,
    ) -> FeedRecord:
        await require_unassigned(db,'FEED',record_id)
        record = await FeedRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FeedRecord with id {record_id} not found.",
            )
            
        await ProductRepo.lock_many(db, [p for p in [record.product_id, request.product_id] if p])
        old_product_id = record.product_id
        old_quantity = record.quantity_used
        new_product_id = request.product_id if request.product_id is not None else old_product_id
        new_quantity = request.quantity_used if request.quantity_used is not None else old_quantity
        
        # Scenario A: Product was changed entirely (Swap)
        if new_product_id != old_product_id:
            # Revert old product
            revert_req = StockMovementCreate(
                product_id=old_product_id,
                movement_type="ADJUSTMENT",
                quantity=old_quantity,
                reference_type="FeedRecord",
                reference_id=record.id
            )
            await StockMovementService.create(db, revert_req, current_user_id, commit=False)
            
            # Check and pull from new product
            new_prod = await ProductRepo.get_by_id(db, new_product_id)
            if not new_prod:
                raise HTTPException(404, "New product not found.")
            if new_prod.current_stock < new_quantity:
                raise HTTPException(400, f"Not enough stock of new product (Needs {new_quantity}, has {new_prod.current_stock})")
                
            pull_req = StockMovementCreate(
                product_id=new_product_id,
                movement_type="OUT",
                quantity=new_quantity,
                reference_type="FeedRecord",
                reference_id=record.id
            )
            await StockMovementService.create(db, pull_req, current_user_id, commit=False)
            await db.refresh(record)
            
        # Scenario B: Same product, quantity changed (Delta)
        elif new_quantity != old_quantity:
            delta = new_quantity - old_quantity
            if delta > 0:
                # We used MORE feed, check stock and OUT
                prod = await ProductRepo.get_by_id(db, old_product_id)
                if prod.current_stock < delta:
                    raise HTTPException(400, f"Not enough stock to increase usage by {delta}. Only {prod.current_stock} available.")
                mov_req = StockMovementCreate(
                    product_id=old_product_id,
                    movement_type="OUT",
                    quantity=delta,
                    reference_type="FeedRecord",
                    reference_id=record.id
                )
                await StockMovementService.create(db, mov_req, current_user_id, commit=False)
                await db.refresh(record)
            elif delta < 0:
                # We used LESS feed, ADJUSTMENT to return the difference
                mov_req = StockMovementCreate(
                    product_id=old_product_id,
                    movement_type="ADJUSTMENT",
                    quantity=abs(delta),
                    reference_type="FeedRecord",
                    reference_id=record.id
                )
                await StockMovementService.create(db, mov_req, current_user_id, commit=False)
                await db.refresh(record)

        update_data = request.model_dump(exclude_unset=True)
        
        # Auto-recalculate total_cost if quantity_used or cost_per_unit changes
        if "total_cost" not in update_data:
            c_qty = update_data.get("quantity_used", record.quantity_used)
            c_cost = update_data.get("cost_per_unit", record.cost_per_unit)
            
            # If product changed and cost wasn't explicitly provided, fetch new product's price
            if new_product_id != old_product_id and "cost_per_unit" not in update_data:
                new_prod = await ProductRepo.get_by_id(db, new_product_id)
                if new_prod:
                    c_cost = new_prod.unit_price
                    update_data["cost_per_unit"] = c_cost
            
            if c_qty is not None and c_cost is not None:
                update_data["total_cost"] = c_qty * c_cost

        updated_record = await FeedRecordRepo.update(db, record, update_data, commit=False)
        await db.refresh(updated_record)
        return updated_record

    @staticmethod
    @atomic
    async def delete(db: AsyncSession, record_id: int, current_user_id: int) -> None:
        await require_unassigned(db,'FEED',record_id)
        record = await FeedRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FeedRecord with id {record_id} not found.",
            )
            
        # Restore stock back to inventory before deleting the record
        if record.product_id:
            restore_req = StockMovementCreate(
                product_id=record.product_id,
                movement_type="ADJUSTMENT",
                quantity=record.quantity_used,
                reference_type="FeedRecord_Deleted",
                reference_id=record.id
            )
            await StockMovementService.create(db, restore_req, current_user_id, commit=False)
            
        await FeedRecordRepo.delete(db, record, commit=False)
