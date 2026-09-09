from fastapi import APIRouter
from app.api.v1.user import roter as user_router
from app.api.v1.farm import router as farm_router

router = APIRouter(
    prefix="/v1"
)

router.include_router(user_router.router)
router.include_router(farm_router.router)