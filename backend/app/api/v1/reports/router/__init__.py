from fastapi import APIRouter

from app.api.v1.reports.router.operations import router as operations_router

router = APIRouter(prefix="/reports", tags=["Reports"])
router.include_router(operations_router)
