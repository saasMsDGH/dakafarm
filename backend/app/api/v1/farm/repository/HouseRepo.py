"""
House repository — all database operations for the House model.

This layer only reads/writes data. No business decisions live here.
"""

from typing import Optional, Tuple, List

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.farm.models.house import House
from app.shared.pagination import PaginationParams


class HouseRepo:
    """Database access layer for the House model."""

    @staticmethod
    async def create_house(db: AsyncSession, house: House) -> House:
        """Persist a new house record. Raises 409 on duplicate name."""
        try:
            db.add(house)
            await db.commit()
            await db.refresh(house)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A house with this name already exists.",
            )
        return house

    @staticmethod
    async def get_by_id(db: AsyncSession, house_id: int) -> Optional[House]:
        """Return a single house by primary key, or None if not found."""
        result = await db.execute(select(House).where(House.id == house_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[House]:
        """Return a single house by name, or None if not found."""
        result = await db.execute(select(House).where(House.name == name))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_houses(
        db: AsyncSession,
        params: PaginationParams,
    ) -> Tuple[List[House], int]:
        """
        Return a paginated, optionally filtered list of houses.

        Search applies to both name and location (case-insensitive).
        Sorting is applied to a valid House column; falls back to created_at.

        Returns:
            (houses, total_count)
        """
        query = select(House)

        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    House.name.ilike(search_term),
                    House.location.ilike(search_term),
                )
            )

        # Count total matching records
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Resolve sort column — default to created_at if column doesn't exist
        sort_column = getattr(House, params.sort_by, House.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        houses = list(result.scalars().all())

        return houses, total

    @staticmethod
    async def update_house(db: AsyncSession, house: House, data: dict) -> House:
        """
        Apply a partial update to a house record.

        Only fields present in `data` are updated (None values are skipped).
        Raises 409 if the updated name conflicts with an existing house.
        """
        for field, value in data.items():
            if value is not None:
                setattr(house, field, value)
        try:
            await db.commit()
            await db.refresh(house)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A house with this name already exists.",
            )
        return house

    @staticmethod
    async def delete_house(db: AsyncSession, house: House) -> None:
        """Permanently delete a house record."""
        await db.delete(house)
        await db.commit()