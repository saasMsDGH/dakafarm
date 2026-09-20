from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.auth.auth import get_current_user
from app.api.v1.user.models import Users
from app.auth.RoleAuth import RoleChecker
from app.api.v1.reports.schemas.operations import FarmOperationsReport
from app.api.v1.reports.service.operations import OperationsReportService

router = APIRouter(
    prefix="/operations",
    tags=["Farm Operations Master Report"],
    redirect_slashes=False
)

report_viewer = RoleChecker(["admin", "farm_manager", "finance_manager"])

@router.get("/master-summary", response_model=FarmOperationsReport)
async def get_master_summary(
    date_from: Optional[datetime] = Query(None, description="Start date for report"),
    date_to: Optional[datetime] = Query(None, description="End date for report"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(report_viewer)
):
    return await OperationsReportService.get_master_summary(db, date_from=date_from, date_to=date_to)
