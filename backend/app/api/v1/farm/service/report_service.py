from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from decimal import Decimal

from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.models.medication_record import MedicationRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.farm.schemas.ReportSchema import FarmReportResponse

async def get_farm_summary_report(db: AsyncSession, start_date: date, end_date: date) -> FarmReportResponse:
    # 1. Production Totals
    prod_query = select(
        func.sum(ProductionRecord.total_eggs).label("total_eggs"),
        func.sum(ProductionRecord.good_eggs).label("good_eggs"),
        func.sum(ProductionRecord.damaged_eggs).label("damaged_eggs")
    ).where(
        ProductionRecord.record_date >= start_date,
        ProductionRecord.record_date <= end_date
    )
    prod_result = await db.execute(prod_query)
    prod_stats = prod_result.first()
    
    total_eggs = int(prod_stats.total_eggs or 0) if prod_stats else 0
    good_eggs = int(prod_stats.good_eggs or 0) if prod_stats else 0
    damaged_eggs = int(prod_stats.damaged_eggs or 0) if prod_stats else 0

    # 2. Mortality Total
    mort_query = select(
        func.sum(MortalityRecord.quantity).label("total_mortality")
    ).where(
        MortalityRecord.record_date >= start_date,
        MortalityRecord.record_date <= end_date
    )
    mort_result = await db.execute(mort_query)
    mort_stats = mort_result.first()
    
    total_mortality = int(mort_stats.total_mortality or 0) if mort_stats else 0

    # 3. Feed Totals
    feed_query = select(
        func.sum(FeedRecord.quantity_used).label("total_feed_used"),
        func.sum(FeedRecord.total_cost).label("total_feed_cost")
    ).where(
        FeedRecord.record_date >= start_date,
        FeedRecord.record_date <= end_date
    )
    feed_result = await db.execute(feed_query)
    feed_stats = feed_result.first()
    
    total_feed_used = Decimal(feed_stats.total_feed_used or 0.0) if feed_stats else Decimal('0.0')
    total_feed_cost = Decimal(feed_stats.total_feed_cost or 0.0) if feed_stats else Decimal('0.0')

    # 4. Medication Totals
    med_query = select(
        func.sum(MedicationRecord.total_cost).label("total_medication_cost")
    ).where(
        MedicationRecord.record_date >= start_date,
        MedicationRecord.record_date <= end_date
    )
    med_result = await db.execute(med_query)
    med_stats = med_result.first()
    
    total_medication_cost = Decimal(med_stats.total_medication_cost or 0.0) if med_stats else Decimal('0.0')

    # 5. Vaccination Totals
    vac_query = select(
        func.sum(VaccinationRecord.total_cost).label("total_vaccination_cost")
    ).where(
        VaccinationRecord.record_date >= start_date,
        VaccinationRecord.record_date <= end_date
    )
    vac_result = await db.execute(vac_query)
    vac_stats = vac_result.first()
    
    total_vaccination_cost = Decimal(vac_stats.total_vaccination_cost or 0.0) if vac_stats else Decimal('0.0')

    # Calculate overall expenses
    total_expenses = total_feed_cost + total_medication_cost + total_vaccination_cost

    return FarmReportResponse(
        start_date=start_date,
        end_date=end_date,
        total_eggs=total_eggs,
        good_eggs=good_eggs,
        damaged_eggs=damaged_eggs,
        total_mortality=total_mortality,
        total_feed_used=total_feed_used,
        total_feed_cost=total_feed_cost,
        total_medication_cost=total_medication_cost,
        total_vaccination_cost=total_vaccination_cost,
        total_expenses=total_expenses
    )
