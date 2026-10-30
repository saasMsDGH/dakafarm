"""
ProductionRecord service — business logic.
"""

from fastapi import HTTPException, status
from app.api.v1.campaigns.service import require_unassigned
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.repository.ProductionRecordRepo import ProductionRecordRepo
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.farm.schemas.ProductionRecordSchema import (
    ProductionRecordCreate,
    ProductionRecordListResponse,
    ProductionRecordUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class ProductionRecordService:
    """Business logic for ProductionRecord."""

    @staticmethod
    def _calculate_automated_fields(total_birds: int, total_eggs: int, damaged_eggs: int) -> tuple[int, Decimal]:
        """
        Calculates good_eggs and laying_percentage.
        Returns: (good_eggs, laying_percentage)
        """
        # Validate logic mathematically to prevent negatives
        good_eggs = max(0, total_eggs - damaged_eggs)
        
        laying_percentage = Decimal("0.00")
        if total_birds > 0:
            percentage = (total_eggs / total_birds) * 100
            
            # Prevent database Numeric(5,2) overflow (max 999.99)
            if percentage >= 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Calculated laying percentage exceeds 999.99%. Please verify that 'total_birds' and 'total_eggs' are correct."
                )
                
            laying_percentage = Decimal(f"{percentage:.2f}")
            
        return good_eggs, laying_percentage

    @staticmethod
    async def create(
        db: AsyncSession,
        request: ProductionRecordCreate,
        current_user_id: int,
    ) -> ProductionRecord:
        """Create a new production record with automated calculations."""
        # 1. Validate Flock exists
        flock = await FlockRepo.get_by_id(db, request.flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {request.flock_id} not found.",
            )

        # 2. Prevent logical errors
        if request.damaged_eggs > request.total_eggs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Damaged eggs cannot exceed total eggs collected.",
            )

        # 3. Auto-calculations
        total_birds = flock.current_quantity
        good_eggs, laying_percentage = ProductionRecordService._calculate_automated_fields(
            total_birds=total_birds,
            total_eggs=request.total_eggs,
            damaged_eggs=request.damaged_eggs,
        )

        new_record = ProductionRecord(
            flock_id=request.flock_id,
            record_date=request.record_date,
            total_birds=total_birds,
            total_eggs=request.total_eggs,
            damaged_eggs=request.damaged_eggs,
            good_eggs=good_eggs,
            laying_percentage=laying_percentage,
            recorded_by=current_user_id,
        )
        return await ProductionRecordRepo.create(db, new_record)

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int) -> ProductionRecord:
        """Return a single production record."""
        record = await ProductionRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductionRecord with id {record_id} not found.",
            )
        return record

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> ProductionRecordListResponse:
        """List paginated production records."""
        records, total = await ProductionRecordRepo.list_records(db, params)
        return ProductionRecordListResponse(
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
        request: ProductionRecordUpdate,
    ) -> ProductionRecord:
        """Update a production record and recalculate derived fields if necessary."""
        await require_unassigned(db,'PRODUCTION',record_id)
        record = await ProductionRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductionRecord with id {record_id} not found.",
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
        
        # Determine values for recalculation
        # Note: total_birds is locked to the original record's total_birds (which captured the state at that time)
        new_total_eggs = update_data.get("total_eggs", record.total_eggs)
        new_damaged_eggs = update_data.get("damaged_eggs", record.damaged_eggs)
        
        # Prevent logical errors
        if new_damaged_eggs > new_total_eggs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Damaged eggs cannot exceed total eggs collected.",
            )

        # Recalculate
        good_eggs, laying_percentage = ProductionRecordService._calculate_automated_fields(
            total_birds=record.bird_days or record.total_birds,
            total_eggs=new_total_eggs,
            damaged_eggs=new_damaged_eggs,
        )
        
        update_data["good_eggs"] = good_eggs
        update_data["laying_percentage"] = laying_percentage

        return await ProductionRecordRepo.update(db, record, update_data)

    @staticmethod
    async def delete(db: AsyncSession, record_id: int) -> None:
        """Delete a production record."""
        await require_unassigned(db,'PRODUCTION',record_id)
        record = await ProductionRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductionRecord with id {record_id} not found.",
            )
        await ProductionRecordRepo.delete(db, record)
