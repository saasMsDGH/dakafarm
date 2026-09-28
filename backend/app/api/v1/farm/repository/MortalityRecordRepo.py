"""
MortalityRecord repository — all database operations for MortalityRecord.
"""

from typing import Optional, Tuple, List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.shared.pagination import PaginationParams


class MortalityRecordRepo:
    """Database access layer for the MortalityRecord model."""

    @staticmethod
    async def create(db: AsyncSession, record: MortalityRecord) -> MortalityRecord:
        """Persist a new mortality record."""
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: int) -> Optional[MortalityRecord]:
        """Return a single mortality record by primary key."""
        result = await db.execute(select(MortalityRecord).where(MortalityRecord.id == record_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_records(
        db: AsyncSession,
        params: PaginationParams,
    ) -> Tuple[List[MortalityRecord], int]:
        """Return a paginated list of mortality records."""
        query = select(MortalityRecord)
        
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Sort
        sort_column = getattr(MortalityRecord, params.sort_by, MortalityRecord.record_date)
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
    async def update(db: AsyncSession, record: MortalityRecord, data: dict) -> MortalityRecord:
        """Apply a partial update."""
        for field, value in data.items():
            if value is not None:
                setattr(record, field, value)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def delete(db: AsyncSession, record: MortalityRecord) -> None:
        """Permanently delete a record."""
        await db.delete(record)
        await db.commit()
