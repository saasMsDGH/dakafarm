from fastapi import APIRouter
from app.api.v1.pos.Router import customer_router

router = APIRouter(prefix="/pos")
router.include_router(customer_router.router)
from app.api.v1.pos.Router import sale_router
router.include_router(sale_router.router)

from app.api.v1.pos.Router import supplier_router
router.include_router(supplier_router.router)
from app.api.v1.pos.Router import purchase_router
router.include_router(purchase_router.router)
from app.api.v1.pos.Router import expense_router
router.include_router(expense_router.router)
