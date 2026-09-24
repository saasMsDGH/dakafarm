from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.schemas.PurchaseSchema import (
    PurchaseCreate,
    PurchaseListResponse,
    PurchaseResponse,
)
from app.api.v1.pos.schemas.PurchasePaymentSchema import PurchasePaymentCreate, PurchasePaymentResponse
from app.api.v1.pos.service.PurchaseService import PurchaseService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.shared.pagination import PaginationParams

pos_manager = RoleChecker(["admin", "sell_manager"])
pos_officer = RoleChecker(["admin", "sell_manager", "sell_officer","inventory_admin"])

router = APIRouter(
    prefix="/purchases",
    tags=["POS Purchases"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new purchase"
)
async def create_purchase(
    request: PurchaseCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> PurchaseResponse:
    return await PurchaseService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=PurchaseListResponse,
    summary="List all purchases"
)
async def list_purchases(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    supplier_id: Optional[int] = Query(default=None),
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> PurchaseListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await PurchaseService.list_purchases(db, params, supplier_id)

@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    summary="Get purchase details by ID"
)
async def get_purchase(
    purchase_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> PurchaseResponse:
    return await PurchaseService.get_purchase(db, purchase_id)

@router.post(
    "/{purchase_id}/payments/",
    response_model=PurchasePaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a payment to a purchase"
)
async def add_purchase_payment(
    purchase_id: int,
    request: PurchasePaymentCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> PurchasePaymentResponse:
    return await PurchaseService.add_payment(db, purchase_id, request, current_user.id)

@router.get(
    "/{purchase_id}/payments/",
    response_model=List[PurchasePaymentResponse],
    summary="List all payments for a purchase"
)
async def list_purchase_payments(
    purchase_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> List[PurchasePaymentResponse]:
    return await PurchaseService.get_payments_for_purchase(db, purchase_id)
