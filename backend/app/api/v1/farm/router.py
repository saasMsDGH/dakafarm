from app.api.v1.farm.Router import house_router, flock_router
from fastapi import APIRouter


router = APIRouter(
    prefix="/farm"
)

router.include_router(house_router.router)
router.include_router(flock_router.router)