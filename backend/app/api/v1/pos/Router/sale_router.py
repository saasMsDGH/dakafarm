from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.schemas.SaleSchema import (
    SaleCreate,
    SaleListResponse,
    SaleResponse,
)
from app.api.v1.pos.schemas.PaymentSchema import PaymentCreate, PaymentResponse
from app.api.v1.pos.service.SaleService import SaleService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

pos_manager = RoleChecker(["admin", "sell_manager"])
pos_officer = RoleChecker(["admin", "sell_manager", "sell_officer"])

router = APIRouter(
    prefix="/sales",
    tags=["POS Sales"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sale (Invoice/Receipt)"
)
async def create_sale(
    request: SaleCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SaleResponse:
    return await SaleService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=SaleListResponse,
    summary="List all sales"
)
async def list_sales(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    customer_id: Optional[int] = Query(default=None),
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SaleListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await SaleService.list_sales(db, params, customer_id)

@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
    summary="Get sale details"
)
async def get_sale(
    sale_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SaleResponse:
    return await SaleService.get_sale(db, sale_id)

@router.post(
    "/{sale_id}/payments/",
    response_model=PaymentResponse,
    summary="Add a payment to a sale (Receipt)"
)
async def add_payment(
    sale_id: int,
    request: PaymentCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    return await SaleService.add_payment(db, sale_id, request, current_user.id)

@router.get(
    "/{sale_id}/payments/",
    response_model=List[PaymentResponse],
    summary="List payments for a sale"
)
async def get_payments(
    sale_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> List[PaymentResponse]:
    return await SaleService.get_payments_for_sale(db, sale_id)
