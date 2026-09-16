from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.schemas.SupplierSchema import (
    SupplierCreate,
    SupplierListResponse,
    SupplierResponse,
    SupplierUpdate,
)
from app.api.v1.pos.service.SupplierService import SupplierService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

pos_manager = RoleChecker(["admin", "sell_manager"])
pos_officer = RoleChecker(["admin", "sell_manager", "sell_officer"])

router = APIRouter(
    prefix="/suppliers",
    tags=["POS Suppliers"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new supplier"
)
async def create_supplier(
    request: SupplierCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    return await SupplierService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=SupplierListResponse,
    summary="List suppliers"
)
async def list_suppliers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=5000),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SupplierListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await SupplierService.list_suppliers(db, params)

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Get a supplier by ID"
)
async def get_supplier(
    supplier_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    return await SupplierService.get_supplier(db, supplier_id)

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse,
    summary="Update a supplier"
)
async def update_supplier(
    supplier_id: int,
    request: SupplierUpdate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    return await SupplierService.update(db, supplier_id, request)

@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a supplier"
)
async def delete_supplier(
    supplier_id: int,
    current_user: Users = Depends(pos_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await SupplierService.delete(db, supplier_id)
