from app.api.v1.campaigns.service import require_unassigned
"""
MortalityRecord service — business logic.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.repository.MortalityRecordRepo import MortalityRecordRepo
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.farm.schemas.MortalityRecordSchema import (
    MortalityRecordCreate,
    MortalityRecordListResponse,
    MortalityRecordUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class MortalityRecordService:
    """Business logic for MortalityRecord."""

    @staticmethod
    async def create(
        db: AsyncSession,
        request: MortalityRecordCreate,
        current_user_id: int,
    ) -> MortalityRecord:
        """Create a new mortality record and update flock quantity."""
        # 1. Fetch flock
        flock = await FlockRepo.get_by_id(db, request.flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {request.flock_id} not found.",
            )

        # 2. Prevent logical errors
        if request.quantity > flock.current_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot log {request.quantity} dead birds. Only {flock.current_quantity} birds are currently in the flock.",
            )

        # 3. Create the record
        new_record = MortalityRecord(
            flock_id=request.flock_id,
            record_date=request.record_date,
            quantity=request.quantity,
            cause=request.cause,
            recorded_by=current_user_id,
        )
        
        # 4. Automate flock current_quantity reduction
        flock.current_quantity -= request.quantity
        # SQLAlchemy will automatically commit the change to flock when we commit the new_record in the repo.
        
        return await MortalityRecordRepo.create(db, new_record)

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int) -> MortalityRecord:
        """Return a single mortality record."""
        record = await MortalityRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MortalityRecord with id {record_id} not found.",
            )
        return record

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> MortalityRecordListResponse:
        """List paginated mortality records."""
        records, total = await MortalityRecordRepo.list_records(db, params)
        return MortalityRecordListResponse(
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
        request: MortalityRecordUpdate,
    ) -> MortalityRecord:
        """Update a mortality record and adjust flock quantity if needed."""
        await require_unassigned(db,'MORTALITY',record_id)
        record = await MortalityRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MortalityRecord with id {record_id} not found.",
            )
            
        # We need the current flock
        flock = await FlockRepo.get_by_id(db, record.flock_id)
            
        # Validate new flock_id if it's changing (complex logic to move birds back and forth)
        if request.flock_id is not None and request.flock_id != record.flock_id:
            new_flock = await FlockRepo.get_by_id(db, request.flock_id)
            if not new_flock:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Flock with id {request.flock_id} not found.",
                )
            
            # Revert old flock
            flock.current_quantity += record.quantity
            
            # Apply to new flock
            new_qty = request.quantity if request.quantity is not None else record.quantity
            if new_qty > new_flock.current_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot log {new_qty} dead birds. Only {new_flock.current_quantity} birds are in the new flock.",
                )
            new_flock.current_quantity -= new_qty
            
        elif request.quantity is not None and request.quantity != record.quantity:
            # Flock stays the same, but quantity changed
            qty_difference = request.quantity - record.quantity
            if qty_difference > flock.current_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot increase mortality beyond the current flock size.",
                )
            flock.current_quantity -= qty_difference

        update_data = request.model_dump(exclude_unset=True)
        return await MortalityRecordRepo.update(db, record, update_data)

    @staticmethod
    async def delete(db: AsyncSession, record_id: int) -> None:
        """Delete a mortality record and restore flock quantity."""
        await require_unassigned(db,'MORTALITY',record_id)
        record = await MortalityRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MortalityRecord with id {record_id} not found.",
            )
            
        # Restore the dead birds to the flock's current_quantity
        flock = await FlockRepo.get_by_id(db, record.flock_id)
        if flock:
            flock.current_quantity += record.quantity
            
        await MortalityRecordRepo.delete(db, record)
