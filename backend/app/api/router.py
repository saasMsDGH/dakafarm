from fastapi import APIRouter
from app.api.v1 import router as v1_router
from app.api.v1.farm import router as farm_v1


router = APIRouter(
    prefix="/api"
)

router.include_router(v1_router.router)
router.include_router(farm_v1.router)