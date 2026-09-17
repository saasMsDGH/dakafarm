from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.assets.models.asset import Asset
from app.shared.pagination import PaginationParams

class AssetRepo:
    @staticmethod
    async def create(db: AsyncSession, asset: Asset) -> Asset:
        try:
            db.add(asset)
            await db.commit()
            await db.refresh(asset)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset with this code might already exist."
            )
        return asset

    @staticmethod
    async def get_by_id(db: AsyncSession, asset_id: int) -> Optional[Asset]:
        result = await db.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_assets(db: AsyncSession, params: PaginationParams) -> Tuple[List[Asset], int]:
        query = select(Asset)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Asset.asset_code.ilike(search_term),
                    Asset.name.ilike(search_term),
                    Asset.serial_number.ilike(search_term),
                    Asset.location.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Asset, params.sort_by, Asset.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        assets = list(result.scalars().all())

        return assets, total

    @staticmethod
    async def update(db: AsyncSession, asset: Asset, data: dict) -> Asset:
        for field, value in data.items():
            if value is not None:
                setattr(asset, field, value)
        try:
            await db.commit()
            await db.refresh(asset)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating asset."
            )
        return asset

    @staticmethod
    async def delete(db: AsyncSession, asset: Asset) -> None:
        try:
            await db.delete(asset)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete asset because it is referenced elsewhere."
            )
