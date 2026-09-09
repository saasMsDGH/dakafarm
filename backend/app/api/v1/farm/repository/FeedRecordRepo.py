"""
FeedRecord repository — all database operations for FeedRecord.
"""

from typing import Optional, Tuple, List

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.farm.models.feed_record import FeedRecord
from app.shared.pagination import PaginationParams


class FeedRecordRepo:
    """Database access layer for the FeedRecord model."""

    @staticmethod
    async def create(db: AsyncSession, record: FeedRecord) -> FeedRecord:
        """Persist a new feed record."""
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: int) -> Optional[FeedRecord]:
        """Return a single feed record by primary key."""
        result = await db.execute(select(FeedRecord).where(FeedRecord.id == record_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> Tuple[List[FeedRecord], int]:
        """Return a paginated list of feed records."""
        query = select(FeedRecord)

        # Basic search logic (since product_id is an integer, search is limited)
        # We can implement specific filters (like flock_id) later if needed.
        # For now, just a simple count and offset/limit.
        
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Sort
        sort_column = getattr(FeedRecord, params.sort_by, FeedRecord.record_date)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Paginate
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        records = list(result.scalars().all())

        return records, total

    @staticmethod
    async def update(db: AsyncSession, record: FeedRecord, data: dict) -> FeedRecord:
        """Apply a partial update."""
        for field, value in data.items():
            if value is not None:
                setattr(record, field, value)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def delete(db: AsyncSession, record: FeedRecord) -> None:
        """Permanently delete a record."""
        await db.delete(record)
        await db.commit()
