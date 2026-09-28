"""
House service — business logic layer for house management.

Responsibilities:
  - Enforce business rules (e.g. cannot delete an occupied house)
  - Coordinate with the repository
  - Raise meaningful HTTP errors for business violations

Does NOT touch the database directly.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.farm.models.house import House
from app.api.v1.farm.repository.HouseRepo import HouseRepo
from app.api.v1.farm.schemas.HouseSchema import (
    HouseCreate,
    HouseListResponse,
    HouseUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages


class HouseService:
    """Business logic for the House resource."""

    @staticmethod
    async def create_house(
        db: AsyncSession,
        request: HouseCreate,
        current_user_id: int,
    ) -> House:
        """
        Create a new house.

        The repository enforces the unique name constraint and raises 409
        on conflict — no need to pre-check here.
        """
        new_house = House(
            name=request.name,
            location=request.location,
            capacity=request.capacity,
            description=request.description,
            created_by=current_user_id,
        )
        return await HouseRepo.create_house(db, new_house)

    @staticmethod
    async def get_house(db: AsyncSession, house_id: int) -> House:
        """Return a house by ID. Raises 404 if not found."""
        house = await HouseRepo.get_by_id(db, house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House with id {house_id} not found.",
            )
        return house

    @staticmethod
    async def list_houses(
        db: AsyncSession,
        params: PaginationParams,
    ) -> HouseListResponse:
        """Return a paginated list of houses, optionally filtered by search term."""
        houses, total = await HouseRepo.list_houses(db, params)
        return HouseListResponse(
            items=houses,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update_house(
        db: AsyncSession,
        house_id: int,
        request: HouseUpdate,
    ) -> House:
        """
        Partially update a house.

        Uses model_dump(exclude_unset=True) so only fields the caller
        explicitly sent are modified.
        """
        house = await HouseRepo.get_by_id(db, house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House with id {house_id} not found.",
            )
        update_data = request.model_dump(exclude_unset=True)
        return await HouseRepo.update_house(db, house, update_data)

    @staticmethod
    async def delete_house(db: AsyncSession, house_id: int) -> None:
        """
        Delete a house.

        Business rule: a house that contains active flocks cannot be deleted.
        NOTE: Once the Flock model is implemented, this guard will be activated.
        """
        house = await HouseRepo.get_by_id(db, house_id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"House with id {house_id} not found.",
            )

        from app.api.v1.farm.repository.FlockRepo import FlockRepo
        
        active_flocks = await FlockRepo.count_active_by_house(db, house_id)
        if active_flocks > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a house that contains active flocks.",
            )

        await HouseRepo.delete_house(db, house)
