from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.schemas.TrialBalanceSchema import TrialBalanceResponse
from app.api.v1.finance.service.TrialBalanceService import TrialBalanceService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/trial-balance",
    tags=["Finance Trial Balance"],
    redirect_slashes=False,
)

@router.get(
    "",
    response_model=TrialBalanceResponse,
    summary="Generate a Trial Balance report",
)
async def get_trial_balance(
    as_of_date: Optional[datetime] = Query(default=None, description="End date for the trial balance (inclusive). If omitted, uses current time."),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> TrialBalanceResponse:
    """
    Generates a mathematically perfect Trial Balance by mapping existing Invoices, Accounts, and Transactions 
    to standard accounting categories (Assets, Liabilities, Equity, Revenue, Expenses).
    """
    return await TrialBalanceService.get_trial_balance(db, as_of_date)
