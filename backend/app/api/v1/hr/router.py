from fastapi import APIRouter
from app.api.v1.hr.Router import employee_router

router = APIRouter(prefix="/hr")
router.include_router(employee_router.router)
from app.api.v1.hr.Router import payroll_router
router.include_router(payroll_router.router)
