import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.assets.models.asset import Asset
from app.api.v1.assets.models.asset_payment import AssetPayment
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.assets.repository.AssetRepo import AssetRepo
from app.api.v1.assets.repository.AssetPaymentRepo import AssetPaymentRepo
from app.api.v1.finance.repository.AccountRepo import AccountRepo
from app.api.v1.assets.schemas.AssetSchema import (
    AssetCreate,
    AssetListResponse,
    AssetUpdate,
    AssetDistributionCreate
)
from app.api.v1.assets.schemas.AssetPaymentSchema import AssetPaymentCreate
from app.shared.pagination import PaginationParams, compute_pages

class AssetService:
    @staticmethod
    def _generate_asset_code() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"AST-{unique_suffix}"

    @staticmethod
    def _generate_payment_reference() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"ASTPAY-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: AssetCreate, current_user_id: int) -> Asset:
        total_cost = request.cost_price * request.quantity
        
        if request.amount_paid > total_cost:
            raise HTTPException(status_code=400, detail="Amount paid cannot exceed total cost.")

        if request.amount_paid > 0:
            if not request.account_id:
                raise HTTPException(status_code=400, detail="account_id is required if amount_paid > 0")
            if not request.payment_method:
                raise HTTPException(status_code=400, detail="payment_method is required if amount_paid > 0")
            
            # Verify account exists
            account = await AccountRepo.get_by_id(db, request.account_id)
            if not account:
                raise HTTPException(status_code=404, detail="Financial account not found.")

        if request.amount_paid == total_cost:
            payment_status = "PAID"
        elif request.amount_paid > 0:
            payment_status = "PARTIAL"
        else:
            payment_status = "UNPAID"

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
            amount_paid=request.amount_paid,
            payment_status=payment_status,
            created_by=current_user_id,
        )
        created_asset = await AssetRepo.create(db, new_asset, commit=False)

        if request.amount_paid > 0:
            # 1. Create AssetPayment
            payment_ref = AssetService._generate_payment_reference()
            asset_payment = AssetPayment(
                asset_id=created_asset.id,
                account_id=request.account_id,
                payment_reference=payment_ref,
                amount=request.amount_paid,
                payment_method=request.payment_method,
                paid_by=current_user_id
            )
            await AssetPaymentRepo.create(db, asset_payment)

            # 2. Create FinancialTransaction
            fin_txn = FinancialTransaction(
                account_id=request.account_id,
                transaction_type="ASSET_PURCHASE",
                direction="OUT",
                amount=request.amount_paid,
                description=f"Payment for Asset {asset_code} - {request.name}",
                reference_number=payment_ref,
                created_by=current_user_id
            )
            db.add(fin_txn)

        try:
            asset_id = created_asset.id
            await db.commit()
            return await AssetRepo.get_by_id(db, asset_id)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

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
    async def create_distribution(db: AsyncSession, asset_id: int, request: AssetDistributionCreate, current_user_id: int):
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

    @staticmethod
    async def add_payment(db: AsyncSession, asset_id: int, request: AssetPaymentCreate, current_user_id: int) -> AssetPayment:
        asset = await AssetRepo.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found.")

        if asset.payment_status == "PAID":
            raise HTTPException(status_code=400, detail="Asset is already fully paid.")

        total_cost = asset.cost_price * asset.quantity
        remaining = total_cost - asset.amount_paid
        if request.amount > remaining:
            raise HTTPException(status_code=400, detail=f"Payment amount exceeds remaining balance of {remaining}.")

        # Verify account
        account = await AccountRepo.get_by_id(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Financial account not found.")

        payment_ref = AssetService._generate_payment_reference()

        # 1. Create AssetPayment
        payment = AssetPayment(
            asset_id=asset.id,
            account_id=request.account_id,
            payment_reference=payment_ref,
            amount=request.amount,
            payment_method=request.payment_method,
            paid_by=current_user_id
        )
        await AssetPaymentRepo.create(db, payment)

        # 2. Update Asset
        asset.amount_paid += request.amount
        if asset.amount_paid >= total_cost:
            asset.payment_status = "PAID"
        else:
            asset.payment_status = "PARTIAL"

        # 3. Create FinancialTransaction
        fin_txn = FinancialTransaction(
            account_id=request.account_id,
            transaction_type="ASSET_PURCHASE",
            direction="OUT",
            amount=request.amount,
            description=f"Payment for Asset {asset.asset_code} - {asset.name}",
            reference_number=payment_ref,
            created_by=current_user_id
        )
        db.add(fin_txn)

        try:
            await db.flush()
            payment_id = payment.id
            await db.commit()
            res = await db.execute(select(AssetPayment).where(AssetPayment.id == payment_id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

    @staticmethod
    async def get_payments_for_asset(db: AsyncSession, asset_id: int) -> list[AssetPayment]:
        return await AssetPaymentRepo.list_payments_for_asset(db, asset_id)
