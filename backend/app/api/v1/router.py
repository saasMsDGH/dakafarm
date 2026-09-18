from fastapi import APIRouter
from app.api.v1.user import router as user_router
from app.api.v1.farm import router as farm_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.pos import router as pos_router
from app.api.v1.hr import router as hr_router
from app.api.v1.assets import router as assets_router
from app.api.v1.finance.Router import account_router
from app.api.v1.finance.Router import transaction_router
from app.api.v1.finance.Router import books_router

router = APIRouter(
    prefix="/v1"
)

router.include_router(user_router.router)
router.include_router(farm_router.router)
router.include_router(inventory_router.router)
router.include_router(pos_router.router)
router.include_router(hr_router.router)
router.include_router(assets_router.router)
router.include_router(account_router.router, prefix="/finance")
router.include_router(transaction_router.router, prefix="/finance")
router.include_router(books_router.router, prefix="/finance")
from app.api.v1.finance.Router.receivables_payables_router import receivables_router, payables_router
from app.api.v1.finance.Router import trial_balance_router, pnl_router, cash_flow_router, balance_sheet_router
router.include_router(receivables_router, prefix="/finance")
router.include_router(payables_router, prefix="/finance")
router.include_router(trial_balance_router.router, prefix="/finance")
router.include_router(pnl_router.router, prefix="/finance")
router.include_router(cash_flow_router.router, prefix="/finance")
router.include_router(balance_sheet_router.router, prefix="/finance")
