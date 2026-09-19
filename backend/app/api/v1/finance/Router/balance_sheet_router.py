from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.schemas.BalanceSheetSchema import BalanceSheetResponse
from app.api.v1.finance.service.BalanceSheetService import BalanceSheetService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/balance-sheet",
    tags=["Finance Balance Sheet"],
    redirect_slashes=False,
)

@router.get(
    "",
    response_model=BalanceSheetResponse,
    summary="Generate a Balance Sheet report",
)
async def get_balance_sheet(
    as_of_date: Optional[datetime] = Query(default=None, description="Optional point in time to snapshot the balance sheet."),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> BalanceSheetResponse:
    """
    Generates a Balance Sheet proving Assets = Liabilities + Equity.
    Automatically calculates Retained Earnings (Net Profit) to bridge the P&L with the balance sheet.
    """
    return await BalanceSheetService.get_balance_sheet(db, as_of_date)
