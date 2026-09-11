"""
VaccinationRecord service — business logic.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.farm.repository.VaccinationRecordRepo import VaccinationRecordRepo
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.farm.schemas.VaccinationRecordSchema import (
    VaccinationRecordCreate,
    VaccinationRecordListResponse,
    VaccinationRecordUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class VaccinationRecordService:
    """Business logic for VaccinationRecord."""

    @staticmethod
    async def create(
        db: AsyncSession,
        request: VaccinationRecordCreate,
        current_user_id: int,
    ) -> VaccinationRecord:
        """Create a new vaccination record with automated cost calculations."""
        # 1. Validate Flock exists
        flock = await FlockRepo.get_by_id(db, request.flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {request.flock_id} not found.",
            )

        # 2. Auto-calculations
        total_cost = None
        if request.cost_per_unit is not None:
            total_cost = request.quantity_used * request.cost_per_unit

        new_record = VaccinationRecord(
            flock_id=request.flock_id,
            product_id=request.product_id,
            record_date=request.record_date,
            disease_targeted=request.disease_targeted,
            administration_method=request.administration_method,
            quantity_used=request.quantity_used,
            cost_per_unit=request.cost_per_unit,
            total_cost=total_cost,
            next_due_date=request.next_due_date,
            recorded_by=current_user_id,
        )
        return await VaccinationRecordRepo.create(db, new_record)

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int) -> VaccinationRecord:
        """Return a single vaccination record."""
        record = await VaccinationRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VaccinationRecord with id {record_id} not found.",
            )
        return record

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> VaccinationRecordListResponse:
        """List paginated vaccination records."""
        records, total = await VaccinationRecordRepo.list_records(db, params)
        return VaccinationRecordListResponse(
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
        request: VaccinationRecordUpdate,
    ) -> VaccinationRecord:
        """Update a vaccination record and recalculate cost if necessary."""
        record = await VaccinationRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VaccinationRecord with id {record_id} not found.",
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
        new_qty = update_data.get("quantity_used", record.quantity_used)
        new_cost = update_data.get("cost_per_unit", record.cost_per_unit)
        
        if new_qty is not None and new_cost is not None:
            update_data["total_cost"] = new_qty * new_cost

        return await VaccinationRecordRepo.update(db, record, update_data)

    @staticmethod
    async def delete(db: AsyncSession, record_id: int) -> None:
        """Delete a vaccination record."""
        record = await VaccinationRecordRepo.get_by_id(db, record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VaccinationRecord with id {record_id} not found.",
            )
        await VaccinationRecordRepo.delete(db, record)
