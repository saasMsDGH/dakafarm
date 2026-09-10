"""
Flock service — business logic layer for flock management.

Responsibilities:
  - Generate flock_code automatically based on House and Date
  - Coordinate with the repository
  - Raise meaningful HTTP errors for business violations
"""

import re
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.repository.FlockRepo import FlockRepo
from app.api.v1.farm.repository.HouseRepo import HouseRepo
from app.api.v1.farm.schemas.FlockSchema import (
    FlockCreate,
    FlockListResponse,
    FlockUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class FlockService:
    """Business logic for the Flock resource."""

    @staticmethod
    async def _generate_flock_code(db: AsyncSession, house_name: str, arrival_date: str) -> str:
        """
        Generates a unique flock code.
        Format: [HOUSENAME]-[YYYYMMDD] (e.g., NORTHBLOCK-20260909)
        If a collision occurs, appends a sequential suffix: NORTHBLOCK-20260909-1
        """
        # Clean house name: remove non-alphanumeric chars and uppercase
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', house_name).upper()
        date_str = arrival_date.replace('-', '')
        
        base_code = f"{clean_name}-{date_str}"
        flock_code = base_code
        
        count = 1
        # Simple loop to ensure uniqueness
        while await FlockRepo.get_by_code(db, flock_code):
            flock_code = f"{base_code}-{count}"
            count += 1
            
        return flock_code

    @staticmethod
    async def create_flock(
        db: AsyncSession,
        request: FlockCreate,
        current_user_id: int,
    ) -> Flock:
        """
        Create a new flock.
        Validates house_id, generates flock_code, and persists.
        """
        # 1. Validate House exists
        house = await HouseRepo.get_by_id(db, request.house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House with id {request.house_id} not found.",
            )

        # 2. Generate Flock Code
        arrival_date_str = request.arrival_date.isoformat()
        flock_code = await FlockService._generate_flock_code(db, house.name, arrival_date_str)

        # 3. Create Flock object
        new_flock = Flock(
            flock_code=flock_code,
            house_id=request.house_id,
            breed=request.breed,
            initial_quantity=request.initial_quantity,
            current_quantity=request.initial_quantity,
            arrival_date=request.arrival_date,
            status=request.status or "active",
            created_by=current_user_id,
        )
        return await FlockRepo.create_flock(db, new_flock)

    @staticmethod
    async def get_flock(db: AsyncSession, flock_id: int) -> Flock:
        """Return a flock by ID. Raises 404 if not found."""
        flock = await FlockRepo.get_by_id(db, flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {flock_id} not found.",
            )
        return flock

    @staticmethod
    async def list_flocks(
        db: AsyncSession,
        params: PaginationParams,
    ) -> FlockListResponse:
        """Return a paginated list of flocks, optionally filtered by search term."""
        flocks, total = await FlockRepo.list_flocks(db, params)
        return FlockListResponse(
            items=flocks,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update_flock(
        db: AsyncSession,
        flock_id: int,
        request: FlockUpdate,
    ) -> Flock:
        """
        Partially update a flock.
        """
        flock = await FlockRepo.get_by_id(db, flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {flock_id} not found.",
            )
            
        # If updating house_id, validate it exists
        if request.house_id is not None and request.house_id != flock.house_id:
            house = await HouseRepo.get_by_id(db, request.house_id)
            if not house:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"House with id {request.house_id} not found.",
                )

        update_data = request.model_dump(exclude_unset=True)
        return await FlockRepo.update_flock(db, flock, update_data)

    @staticmethod
    async def delete_flock(db: AsyncSession, flock_id: int) -> None:
        """
        Delete a flock.
        """
        flock = await FlockRepo.get_by_id(db, flock_id)
        if not flock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flock with id {flock_id} not found.",
            )

        await FlockRepo.delete_flock(db, flock)
