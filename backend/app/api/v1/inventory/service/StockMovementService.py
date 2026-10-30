from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.inventory.repository.StockMovementRepo import StockMovementRepo
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.inventory.schemas.StockMovementSchema import (
    StockMovementCreate,
    StockMovementListResponse,
)
from app.shared.pagination import PaginationParams, compute_pages
import datetime
from decimal import Decimal, ROUND_HALF_UP

class StockMovementService:
    @staticmethod
    async def create(db: AsyncSession, request: StockMovementCreate, current_user_id: int, commit: bool = True, purchase_valued: bool = False) -> StockMovement:
        # Conserver le CUMP calculé dans la même transaction avant le rechargement verrouillé.
        await db.flush()
        product = await ProductRepo.get_by_id(db, request.product_id, for_update=True)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {request.product_id} not found."
            )

        cost = product.unit_price
        basis = product.cost_basis
        if request.movement_type in {"IN", "ADJUSTMENT"} and not purchase_valued:
            product.cost_basis = "UNVERIFIED"

        # Apply stock math securely
        if request.movement_type == "IN":
            product.current_stock += request.quantity
        elif request.movement_type == "OUT":
            if product.current_stock < request.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot move OUT {request.quantity}. Only {product.current_stock} available."
                )
            product.current_stock -= request.quantity
        elif request.movement_type == "ADJUSTMENT":
            if product.current_stock + request.quantity < 0:
                raise HTTPException(422, "Un ajustement ne peut pas rendre le stock négatif.")
            product.current_stock += request.quantity

        movement = StockMovement(
            product_id=request.product_id,
            movement_type=request.movement_type,
            quantity=request.quantity,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            movement_date=request.movement_date or datetime.datetime.now(datetime.timezone.utc),
            unit_cost_snapshot=cost if request.movement_type == "OUT" else None,
            valuation_basis=basis if request.movement_type == "OUT" else None,
            cost_total_fcfa=int((request.quantity * cost).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                if request.movement_type == "OUT" and basis in {"DECLARED", "WEIGHTED_AVERAGE"} and cost is not None else None,
            created_by=current_user_id
        )

        created_movement = await StockMovementRepo.create(db, movement)
        
        # Commit both the movement and the product update simultaneously
        try:
            if commit:
                await db.commit()
                await db.refresh(created_movement)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database transaction failed")
            
        return created_movement

    @staticmethod
    async def get_movement(db: AsyncSession, movement_id: int) -> StockMovement:
        movement = await StockMovementRepo.get_by_id(db, movement_id)
        if not movement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"StockMovement with id {movement_id} not found."
            )
        return movement

    @staticmethod
    async def list_movements(
        db: AsyncSession, 
        params: PaginationParams, 
        product_id: int = None,
        movement_type: str = None
    ) -> StockMovementListResponse:
        movements, total = await StockMovementRepo.list_movements(db, params, product_id, movement_type)
        return StockMovementListResponse(
            items=movements,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

