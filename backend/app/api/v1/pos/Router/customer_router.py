from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.schemas.CustomerSchema import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.api.v1.pos.service.CustomerService import CustomerService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.auth.auth import get_current_user
from app.core.database import get_db
from app.shared.pagination import PaginationParams

pos_manager = RoleChecker(["admin", "sell_manager"])
pos_officer = RoleChecker(["admin", "sell_manager", "sell_officer"])

router = APIRouter(
    prefix="/customers",
    tags=["POS Customers"],
    redirect_slashes=False,
)

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer"
)
async def create_customer(
    request: CustomerCreate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.create(db, request, current_user.id)

@router.get(
    "/",
    response_model=CustomerListResponse,
    summary="List customers"
)
async def list_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> CustomerListResponse:
    params = PaginationParams(
        page=page, limit=limit, search=search, sort_by=sort_by, order=order
    )
    return await CustomerService.list_customers(db, params)

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get a customer by ID"
)
async def get_customer(
    customer_id: int,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.get_customer(db, customer_id)

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update a customer"
)
async def update_customer(
    customer_id: int,
    request: CustomerUpdate,
    current_user: Users = Depends(pos_officer),
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    return await CustomerService.update(db, customer_id, request)

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a customer"
)
async def delete_customer(
    customer_id: int,
    current_user: Users = Depends(pos_manager),
    db: AsyncSession = Depends(get_db),
) -> None:
    await CustomerService.delete(db, customer_id)
