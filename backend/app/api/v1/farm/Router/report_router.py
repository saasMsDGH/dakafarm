from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.core.database import get_db
from app.auth.RoleAuth import RoleChecker
from app.api.v1.user.models import Users

manage_house = RoleChecker(["admin", "Farm Manager"])

from app.api.v1.farm.schemas.ReportSchema import FarmReportResponse
from app.api.v1.farm.service.report_service import get_farm_summary_report

router = APIRouter(
    prefix="/reports",
    tags=["Farm Reports"],
    redirect_slashes=False,
)

@router.get("/summary", response_model=FarmReportResponse)
async def get_report_summary(
    start_date: date = Query(..., description="Start date for the report range"),
    end_date: date = Query(..., description="End date for the report range"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(manage_house)
):
    """
    Retrieve a summarized report for all farm operations (production, mortality, feed, meds, vaccines)
    within the specified date range.
    """
    report = await get_farm_summary_report(db=db, start_date=start_date, end_date=end_date)
    return report
