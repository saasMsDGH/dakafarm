import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.assets.models.asset import Asset
from app.api.v1.assets.repository.AssetRepo import AssetRepo
from app.api.v1.assets.schemas.AssetSchema import (
    AssetCreate,
    AssetListResponse,
    AssetUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class AssetService:
    @staticmethod
    def _generate_asset_code() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"AST-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: AssetCreate, current_user_id: int) -> Asset:
        asset_code = AssetService._generate_asset_code()
        
        new_asset = Asset(
            asset_code=asset_code,
            name=request.name,
            description=request.description,
            purchase_date=request.purchase_date,
            cost_price=request.cost_price,
            quantity=request.quantity,
            condition=request.condition,
            depreciation_rate=request.depreciation_rate,
            status=request.status,
            created_by=current_user_id,
        )
        return await AssetRepo.create(db, new_asset)

    @staticmethod
    async def get_asset(db: AsyncSession, asset_id: int) -> Asset:
        asset = await AssetRepo.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found."
            )
        return asset

    @staticmethod
    async def list_assets(db: AsyncSession, params: PaginationParams) -> AssetListResponse:
        assets, total = await AssetRepo.list_assets(db, params)
        return AssetListResponse(
            items=assets,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, asset_id: int, request: AssetUpdate) -> Asset:
        asset = await AssetRepo.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await AssetRepo.update(db, asset, update_data)


    @staticmethod
    async def create_distribution(db: AsyncSession, asset_id: int, request: "AssetDistributionCreate", current_user_id: int):
        asset = await AssetRepo.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")
        
        # Optionally validate if sum of distributions exceeds asset.quantity
        from app.api.v1.assets.models.asset import AssetDistribution
        new_dist = AssetDistribution(
            asset_id=asset.id,
            location=request.location,
            quantity=request.quantity,
            assigned_date=request.assigned_date,
            notes=request.notes,
            created_by=current_user_id
        )
        return await AssetRepo.create_distribution(db, new_dist)

    @staticmethod
    async def delete(db: AsyncSession, asset_id: int) -> None:
        asset = await AssetRepo.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found."
            )
        await AssetRepo.delete(db, asset)
