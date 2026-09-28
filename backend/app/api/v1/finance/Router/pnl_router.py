from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.schemas.PnLSchema import PnLResponse
from app.api.v1.finance.service.PnLService import PnLService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/pnl",
    tags=["Finance Profit & Loss"],
    redirect_slashes=False,
)

@router.get(
    "",
    response_model=PnLResponse,
    summary="Generate a Profit & Loss (Income Statement) report",
)
async def get_pnl(
    start_date: Optional[datetime] = Query(default=None, description="Start date for the P&L period (inclusive)."),
    end_date: Optional[datetime] = Query(default=None, description="End date for the P&L period (inclusive)."),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> PnLResponse:
    """
    Generates a Multi-Step Profit & Loss statement based on operating revenue, 
    cost of goods sold, operating expenses, and non-operating income/expenses.
    """
    return await PnLService.get_pnl(db, start_date, end_date)
