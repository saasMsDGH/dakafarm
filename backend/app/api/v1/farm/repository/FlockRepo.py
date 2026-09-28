"""
Flock repository — all database operations for the Flock model.

This layer only reads/writes data. No business decisions live here.
"""

from typing import Optional, Tuple, List

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.farm.models.flock import Flock
from app.shared.pagination import PaginationParams


class FlockRepo:
    """Database access layer for the Flock model."""

    @staticmethod
    async def create_flock(db: AsyncSession, flock: Flock) -> Flock:
        """Persist a new flock record. Raises 409 on duplicate flock_code."""
        try:
            db.add(flock)
            await db.commit()
            await db.refresh(flock)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A flock with this flock_code already exists.",
            )
        return flock

    @staticmethod
    async def get_by_id(db: AsyncSession, flock_id: int) -> Optional[Flock]:
        """Return a single flock by primary key, or None if not found."""
        result = await db.execute(select(Flock).where(Flock.id == flock_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, flock_code: str) -> Optional[Flock]:
        """Return a single flock by flock_code, or None if not found."""
        result = await db.execute(select(Flock).where(Flock.flock_code == flock_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_flocks(
        db: AsyncSession,
        params: PaginationParams,
    ) -> Tuple[List[Flock], int]:
        """
        Return a paginated, optionally filtered list of flocks.

        Search applies to flock_code, breed, and status (case-insensitive).
        """
        query = select(Flock)

        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Flock.flock_code.ilike(search_term),
                    Flock.breed.ilike(search_term),
                    Flock.status.ilike(search_term),
                )
            )

        # Count total matching records
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Resolve sort column — default to created_at if column doesn't exist
        sort_column = getattr(Flock, params.sort_by, Flock.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        flocks = list(result.scalars().all())

        return flocks, total

    @staticmethod
    async def update_flock(db: AsyncSession, flock: Flock, data: dict) -> Flock:
        """
        Apply a partial update to a flock record.
        Only fields present in `data` are updated.
        """
        for field, value in data.items():
            if value is not None:
                setattr(flock, field, value)
        try:
            await db.commit()
            await db.refresh(flock)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A flock with this code already exists or there is a database constraint error.",
            )
        return flock

    @staticmethod
    async def delete_flock(db: AsyncSession, flock: Flock) -> None:
        """Permanently delete a flock record."""
        await db.delete(flock)
        await db.commit()
        
    @staticmethod
    async def count_active_by_house(db: AsyncSession, house_id: int) -> int:
        """Return the number of active flocks in a specific house."""
        query = select(func.count()).select_from(Flock).where(
            Flock.house_id == house_id,
            Flock.status == "Active"
        )
        result = await db.execute(query)
        return result.scalar() or 0
