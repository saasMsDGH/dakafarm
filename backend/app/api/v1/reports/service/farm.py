from __future__ import annotations
from decimal import Decimal

from app.api.v1.reports.repository.farm import FarmReportRepo
from app.api.v1.reports.schemas.farm import (
    ProductionSummaryReport, ProductionRecordItem, ProductionByFlockItem, ProductionByHouseItem,
    FeedUsageReport, FeedUsageItem, FeedByFlockItem, MedicationReport, MedicationItem,
    VaccinationReport, VaccinationItem, MortalitySummaryReport, MortalityByFlockItem, MortalityByCauseItem,
)
from app.shared.pagination import compute_pages


class FarmReportService:

    @staticmethod
    async def production_summary(db, params, flock_id=None, house_id=None, date_from=None, date_to=None):
        items, total, total_eggs, good, damaged, avg_pct = await FarmReportRepo.production_detail(
            db, params, flock_id, house_id, date_from, date_to)
        return ProductionSummaryReport(
            items=[ProductionRecordItem(**i) for i in items], total=total,
            page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
            total_eggs=total_eggs, total_good_eggs=good, total_damaged_eggs=damaged, avg_laying_pct=avg_pct,
        )

    @staticmethod
    async def production_by_flock(db, date_from=None, date_to=None):
        rows = await FarmReportRepo.production_by_flock(db, date_from, date_to)
        return [ProductionByFlockItem(**r) for r in rows]

    @staticmethod
    async def production_by_house(db, date_from=None, date_to=None):
        rows = await FarmReportRepo.production_by_house(db, date_from, date_to)
        return [ProductionByHouseItem(**r) for r in rows]

    @staticmethod
    async def feed_usage(db, params, flock_id=None, product_id=None, date_from=None, date_to=None):
        items, total, total_qty, total_cost = await FarmReportRepo.feed_usage(db, params, flock_id, product_id, date_from, date_to)
        return FeedUsageReport(
            items=[FeedUsageItem(**i) for i in items], total=total,
            page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
            total_cost=total_cost, total_quantity_used=total_qty,
        )

    @staticmethod
    async def feed_by_flock(db, date_from=None, date_to=None):
        rows = await FarmReportRepo.feed_by_flock(db, date_from, date_to)
        return [FeedByFlockItem(**r) for r in rows]

    @staticmethod
    async def medication(db, params, flock_id=None, date_from=None, date_to=None):
        items, total, total_cost = await FarmReportRepo.medication(db, params, flock_id, date_from, date_to)
        return MedicationReport(
            items=[MedicationItem(**i) for i in items], total=total,
            page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
            total_cost=total_cost,
        )

    @staticmethod
    async def vaccination(db, params, flock_id=None, date_from=None, date_to=None):
        items, total = await FarmReportRepo.vaccination(db, params, flock_id, date_from, date_to)
        return VaccinationReport(
            items=[VaccinationItem(**i) for i in items], total=total,
            page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def upcoming_vaccinations(db, days_ahead=30):
        rows = await FarmReportRepo.upcoming_vaccinations(db, days_ahead)
        return [VaccinationItem(**r) for r in rows]

    @staticmethod
    async def mortality_summary(db, date_from=None, date_to=None):
        data = await FarmReportRepo.mortality_summary(db, date_from, date_to)
        return MortalitySummaryReport(
            total_deaths=data['total_deaths'],
            num_flocks_affected=data['num_flocks_affected'],
            period_from=str(date_from.date()) if date_from else None,
            period_to=str(date_to.date()) if date_to else None,
        )

    @staticmethod
    async def mortality_by_flock(db, date_from=None, date_to=None):
        rows = await FarmReportRepo.mortality_by_flock(db, date_from, date_to)
        return [MortalityByFlockItem(**r) for r in rows]

    @staticmethod
    async def mortality_by_cause(db, date_from=None, date_to=None):
        rows = await FarmReportRepo.mortality_by_cause(db, date_from, date_to)
        return [MortalityByCauseItem(**r) for r in rows]
