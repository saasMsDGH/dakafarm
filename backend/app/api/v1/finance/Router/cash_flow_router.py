from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.schemas.CashFlowSchema import CashFlowResponse
from app.api.v1.finance.service.CashFlowService import CashFlowService
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db

finance_manager = RoleChecker(["admin", "finance_manager"])

router = APIRouter(
    prefix="/cash-flow",
    tags=["Finance Cash Flow"],
    redirect_slashes=False,
)

@router.get(
    "",
    response_model=CashFlowResponse,
    summary="Generate a Statement of Cash Flows",
)
async def get_cash_flow(
    start_date: Optional[datetime] = Query(default=None, description="Start date for the period (inclusive)."),
    end_date: Optional[datetime] = Query(default=None, description="End date for the period (inclusive)."),
    current_user: Users = Depends(finance_manager),
    db: AsyncSession = Depends(get_db),
) -> CashFlowResponse:
    """
    Generates a Cash Flow statement based on actual cash movements in the ledger, 
    divided into Operating, Investing, and Financing activities.
    """
    return await CashFlowService.get_cash_flow(db, start_date, end_date)
