from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.schemas.DashboardSchema import FinanceDashboardResponse
from app.api.v1.finance.service.DashboardService import DashboardService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db

# Dashboards often need to be viewed by more than just finance managers (e.g. owners/admins).
# The RoleChecker typically covers this if 'admin' is included.
finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/dashboard",
    tags=["Finance Dashboard"],
    redirect_slashes=False,
)

@router.get(
    "",
    response_model=FinanceDashboardResponse,
    summary="Get High-Level Finance KPIs",
)
async def get_dashboard_metrics(
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> FinanceDashboardResponse:
    """
    Returns the top-level KPIs required for the Finance Admin Dashboard cards.
    Calculates lifetime balances for assets/liabilities and current-month performance for profit.
    """
    return await DashboardService.get_dashboard_metrics(db)
