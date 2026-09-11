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

class ProductService:
    @staticmethod
    async def create(db: AsyncSession, request: ProductCreate, current_user_id: int) -> Product:
        # Validate Category

        name = await ProductRepo.get_by_name(db,product_name=request.name)

        if name :
            raise HTTPException(status_code=409,detail="product with that name already exisist")
        
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
            reorder_level=request.reorder_level,
            description=request.description,
            is_active=request.is_active,
            created_by=current_user_id,
        )
        return await ProductRepo.create(db, new_product)

    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Product:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found.",
            )
        return product

    @staticmethod
    async def list_products(db: AsyncSession, params: PaginationParams, category_id: int = None) -> ProductListResponse:
        products, total = await ProductRepo.list_products(db, params, category_id)
        return ProductListResponse(
            items=products,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, product_id: int, request: ProductUpdate) -> Product:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found.",
            )
        
        # Validate Category if provided
        if request.category_id is not None and request.category_id != product.category_id:
            category = await ProductCategoryRepo.get_by_id(db, request.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ProductCategory with id {request.category_id} not found.",
                )

        update_data = request.model_dump(exclude_unset=True)
        return await ProductRepo.update(db, product, update_data)

    @staticmethod
    async def delete(db: AsyncSession, product_id: int) -> None:
        product = await ProductRepo.get_by_id(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found.",
            )
        await ProductRepo.delete(db, product)
