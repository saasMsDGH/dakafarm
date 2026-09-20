from fastapi import APIRouter

from app.api.v1.reports.router.financial import router as financial_router
from app.api.v1.reports.router.sales import router as sales_router
from app.api.v1.reports.router.purchases import router as purchases_router
from app.api.v1.reports.router.expenses import router as expenses_router
from app.api.v1.reports.router.inventory import router as inventory_router
from app.api.v1.reports.router.farm import router as farm_router
from app.api.v1.reports.router.hr import router as hr_router
from app.api.v1.reports.router.assets import router as assets_router
from app.api.v1.reports.router.management import router as management_router

router = APIRouter(prefix="/reports", tags=["Reports"])

router.include_router(financial_router)
router.include_router(sales_router)
router.include_router(purchases_router)
router.include_router(expenses_router)
router.include_router(inventory_router)
router.include_router(farm_router)
router.include_router(hr_router)
router.include_router(assets_router)
router.include_router(management_router)
