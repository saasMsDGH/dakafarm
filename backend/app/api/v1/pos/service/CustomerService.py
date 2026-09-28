import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.repository.CustomerRepo import CustomerRepo
from app.api.v1.pos.schemas.CustomerSchema import (
    CustomerCreate,
    CustomerListResponse,
    CustomerUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class CustomerService:
    @staticmethod
    def _generate_customer_code() -> str:
        # Generates a unique, short code for the customer, e.g. CUST-A1B2C3
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"CUST-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: CustomerCreate, current_user_id: int) -> Customer:
        customer_code = CustomerService._generate_customer_code()
        
        new_customer = Customer(
            customer_code=customer_code,
            name=request.name,
            business_type=request.business_type,
            phone=request.phone,
            email=request.email,
            address=request.address,
            credit_limit=request.credit_limit,
            created_by=current_user_id,
        )
        return await CustomerRepo.create(db, new_customer)

    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
        customer = await CustomerRepo.get_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with id {customer_id} not found."
            )
        return customer

    @staticmethod
    async def list_customers(db: AsyncSession, params: PaginationParams) -> CustomerListResponse:
        customers, total = await CustomerRepo.list_customers(db, params)
        return CustomerListResponse(
            items=customers,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, customer_id: int, request: CustomerUpdate) -> Customer:
        customer = await CustomerRepo.get_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with id {customer_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await CustomerRepo.update(db, customer, update_data)

    @staticmethod
    async def delete(db: AsyncSession, customer_id: int) -> None:
        customer = await CustomerRepo.get_by_id(db, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with id {customer_id} not found."
            )
        await CustomerRepo.delete(db, customer)
