from fastapi import APIRouter
from app.api.v1.farm.Router import (
    house_router, 
    flock_router, 
    feed_record_router, 
    production_record_router, 
    mortality_record_router,
    medication_record_router,
    vaccination_record_router,
    report_router
)

router = APIRouter(
    prefix="/farm"
)

router.include_router(house_router.router)
router.include_router(flock_router.router)
router.include_router(feed_record_router.router)
router.include_router(production_record_router.router)
router.include_router(mortality_record_router.router)
router.include_router(medication_record_router.router)
router.include_router(vaccination_record_router.router)
router.include_router(report_router.router)