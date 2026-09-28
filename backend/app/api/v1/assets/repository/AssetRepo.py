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
    async def create(db: AsyncSession, asset: Asset, commit: bool = True) -> Asset:
        try:
            db.add(asset)
            if commit:
                await db.commit()
                await db.refresh(asset)
                return await AssetRepo.get_by_id(db, asset.id)
            else:
                await db.flush()
                return asset
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset with this code might already exist."
            )

    @staticmethod
    async def get_by_id(db: AsyncSession, asset_id: int) -> Optional[Asset]:
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Asset)
            .options(selectinload(Asset.distributions))
            .where(Asset.id == asset_id)
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_assets(db: AsyncSession, params: PaginationParams) -> Tuple[List[Asset], int]:
        query = select(Asset)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Asset.asset_code.ilike(search_term),
                    Asset.name.ilike(search_term)
                )
            )

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(Asset, params.sort_by, Asset.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        from sqlalchemy.orm import selectinload
        query = query.options(selectinload(Asset.distributions)).offset(params.offset).limit(params.limit)
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
        return await AssetRepo.get_by_id(db, asset.id)


    @staticmethod
    async def create_distribution(db: AsyncSession, distribution: "AssetDistribution") -> "AssetDistribution":
        db.add(distribution)
        await db.commit()
        await db.refresh(distribution)
        return distribution

    @staticmethod
    async def get_distributions(db: AsyncSession, asset_id: int):
        from app.api.v1.assets.models.asset import AssetDistribution
        result = await db.execute(select(AssetDistribution).where(AssetDistribution.asset_id == asset_id))
        return result.scalars().all()

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
