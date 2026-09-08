from app.api.v1.farm.Router import house_router
from fastapi import APIRouter


router = APIRouter(
    prefix="/v1"
)

router.include_router(house_router.router)