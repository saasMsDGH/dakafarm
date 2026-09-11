from fastapi import APIRouter
from app.api.v1.inventory.Router import product_category_router

router = APIRouter(
    prefix="/inventory"
)

router.include_router(product_category_router.router)
