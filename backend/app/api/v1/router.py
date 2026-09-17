from fastapi import APIRouter
from app.api.v1.user import router as user_router
from app.api.v1.farm import router as farm_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.pos import router as pos_router

router = APIRouter(
    prefix="/v1"
)

router.include_router(user_router.router)
router.include_router(farm_router.router)
router.include_router(inventory_router.router)
router.include_router(pos_router.router)
