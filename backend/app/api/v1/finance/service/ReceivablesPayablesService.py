from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.ReceivablesPayablesRepo import ReceivablesPayablesRepo
from app.api.v1.finance.schemas.ReceivablesPayablesSchema import (
    ReceivablesSummaryResponse,
    CustomerReceivablesDetailResponse,
    PayablesSummaryResponse,
    SupplierPayablesDetailResponse
)
from app.shared.pagination import PaginationParams, compute_pages

class ReceivablesPayablesService:
    @staticmethod
    async def get_receivables_summary(db: AsyncSession, params: PaginationParams) -> ReceivablesSummaryResponse:
        items, total_count, total_outstanding = await ReceivablesPayablesRepo.get_receivables_summary(db, params)
        return ReceivablesSummaryResponse(
            items=items,
            total_outstanding=total_outstanding,
            total=total_count,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total_count, params.limit)
        )

    @staticmethod
    async def get_customer_receivables_detail(db: AsyncSession, customer_id: int) -> CustomerReceivablesDetailResponse:
        customer, sales, total_outstanding = await ReceivablesPayablesRepo.get_customer_receivables_detail(db, customer_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer {customer_id} not found.")
        
        return CustomerReceivablesDetailResponse(
            customer_id=customer.id,
            customer_name=customer.name,
            total_outstanding=total_outstanding,
            sales=sales
        )

    @staticmethod
    async def get_payables_summary(db: AsyncSession, params: PaginationParams) -> PayablesSummaryResponse:
        items, total_count, total_outstanding = await ReceivablesPayablesRepo.get_payables_summary(db, params)
        return PayablesSummaryResponse(
            items=items,
            total_outstanding=total_outstanding,
            total=total_count,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total_count, params.limit)
        )

    @staticmethod
    async def get_supplier_payables_detail(db: AsyncSession, supplier_id: int) -> SupplierPayablesDetailResponse:
        supplier, purchases, total_outstanding = await ReceivablesPayablesRepo.get_supplier_payables_detail(db, supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Supplier {supplier_id} not found.")
        
        return SupplierPayablesDetailResponse(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            total_outstanding=total_outstanding,
            purchases=purchases
        )
