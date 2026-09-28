import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.pos.repository.SupplierRepo import SupplierRepo
from app.api.v1.pos.schemas.SupplierSchema import (
    SupplierCreate,
    SupplierListResponse,
    SupplierUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class SupplierService:
    @staticmethod
    def _generate_supplier_code() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"SUPP-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: SupplierCreate, current_user_id: int) -> Supplier:
        supplier_code = SupplierService._generate_supplier_code()

        new_supplier = Supplier(
            supplier_code=supplier_code,
            name=request.name,
            contact_person=request.contact_person,
            phone=request.phone,
            email=request.email,
            address=request.address,
            created_by=current_user_id,
        )
        return await SupplierRepo.create(db, new_supplier)

    @staticmethod
    async def get_supplier(db: AsyncSession, supplier_id: int) -> Supplier:
        supplier = await SupplierRepo.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found."
            )
        return supplier

    @staticmethod
    async def list_suppliers(db: AsyncSession, params: PaginationParams) -> SupplierListResponse:
        suppliers, total = await SupplierRepo.list_suppliers(db, params)
        return SupplierListResponse(
            items=suppliers,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, supplier_id: int, request: SupplierUpdate) -> Supplier:
        supplier = await SupplierRepo.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await SupplierRepo.update(db, supplier, update_data)

    @staticmethod
    async def delete(db: AsyncSession, supplier_id: int) -> None:
        supplier = await SupplierRepo.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {supplier_id} not found."
            )
        await SupplierRepo.delete(db, supplier)
