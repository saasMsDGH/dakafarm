from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.inventory.repository.ProductCategoryRepo import ProductCategoryRepo
from app.api.v1.inventory.schemas.ProductSchema import (
    ProductCreate,
    ProductListResponse,
    ProductUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages
from app.api.v1.inventory.schemas.StockMovementSchema import StockMovementCreate
from app.api.v1.inventory.service.StockMovementService import StockMovementService

class ProductService:
    @staticmethod
    async def create(db: AsyncSession, request: ProductCreate, current_user_id: int) -> Product:
        name = await ProductRepo.get_by_name(db,product_name=request.name)
        if name :
            raise HTTPException(status_code=409,detail="product with that name already exist")
        
        category = await ProductCategoryRepo.get_by_id(db, request.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ProductCategory with id {request.category_id} not found.",
            )

        new_product = Product(
            name=request.name,
            category_id=request.category_id,
            unit_of_measure=request.unit_of_measure,
            unit_price=request.unit_price,
            selling_price=request.selling_price,
            reorder_level=request.reorder_level,
            description=request.description,
            is_active=request.is_active,
            current_stock=0,
            created_by=current_user_id,
        )
        # Use add and flush to keep in same transaction
        db.add(new_product)
        await db.flush()

        if request.current_stock is not None and request.current_stock > 0:
            movement = StockMovementCreate(
                product_id=new_product.id,
                movement_type="IN",
                quantity=request.current_stock,
                reference_type="Initial Stock",
                reference_id=new_product.id
            )
            # Use commit=False so we control the transaction
            await StockMovementService.create(db, movement, current_user_id, commit=False)

        await db.commit()
        await db.refresh(new_product)
        db.expunge(new_product)
        return new_product

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Product:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
        return product

    @staticmethod
    async def list_products(db: AsyncSession, params: PaginationParams, category_id: int = None) -> ProductListResponse:
        products, total = await ProductRepo.list_products(db, params, category_id)
        return ProductListResponse(
            items=products, total=total, page=params.page, limit=params.limit, pages=compute_pages(total, params.limit)
        )

    @staticmethod
    async def update(db: AsyncSession, product_id: int, request: ProductUpdate, current_user_id: int = 1) -> Product:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
        
        if request.category_id is not None and request.category_id != product.category_id:
            category = await ProductCategoryRepo.get_by_id(db, request.category_id)
            if not category:
                raise HTTPException(status_code=404, detail=f"ProductCategory with id {request.category_id} not found.")

        update_data = request.model_dump(exclude_unset=True)
        
        if "current_stock" in update_data:
            new_stock = update_data.pop("current_stock")
            if new_stock is not None:
                diff = new_stock - product.current_stock
                if diff != 0:
                    m_type = "IN" if diff > 0 else "OUT"
                    movement = StockMovementCreate(
                        product_id=product.id,
                        movement_type=m_type,
                        quantity=abs(diff),
                        reference_type="Manual Adjustment",
                        reference_id=product.id
                    )
                    await StockMovementService.create(db, movement, current_user_id, commit=False)
                
        for field, value in update_data.items():
            if value is not None:
                setattr(product, field, value)
                
        await db.commit()
        await db.refresh(product)
        db.expunge(product)
        return product

    @staticmethod
    async def delete(db: AsyncSession, product_id: int) -> None:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
        await ProductRepo.delete(db, product)
