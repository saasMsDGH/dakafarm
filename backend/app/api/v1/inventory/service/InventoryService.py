from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.inventory.schemas.InventorySchema import InventoryResponse, InventoryListResponse
from app.shared.pagination import PaginationParams, compute_pages
from decimal import Decimal

class InventoryService:
    @staticmethod
    def _calculate_status(quantity: Decimal, reorder_level: Decimal) -> str:
        if quantity <= 0:
            return "Out of Stock"
        elif quantity <= reorder_level:
            return "Low Stock"
        return "In Stock"

    @staticmethod
    async def get_inventory_status(db: AsyncSession, product_id: int) -> InventoryResponse:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found."
            )
            
        return InventoryResponse(
            product_id=product.id,
            product_name=product.name,
            unit_of_measure=product.unit_of_measure,
            quantity=product.current_stock,
            reorder_level=product.reorder_level,
            status=InventoryService._calculate_status(product.current_stock, product.reorder_level),
            updated_at=product.updated_at
        )

    @staticmethod
    async def list_inventory(db: AsyncSession, params: PaginationParams, category_id: int = None, status_filter: str = None) -> InventoryListResponse:
        products, total = await ProductRepo.list_products(db, params, category_id, status_filter)
        
        items = []
        for p in products:
            inv_status = InventoryService._calculate_status(p.current_stock, p.reorder_level)
            
            items.append(InventoryResponse(
                product_id=p.id,
                product_name=p.name,
                unit_of_measure=p.unit_of_measure,
                quantity=p.current_stock,
                reorder_level=p.reorder_level,
                status=inv_status,
                updated_at=p.updated_at
            ))

        return InventoryListResponse(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )
