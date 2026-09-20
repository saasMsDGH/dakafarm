from __future__ import annotations
from decimal import Decimal

from app.api.v1.reports.repository.assets import AssetsReportRepo
from app.api.v1.reports.schemas.assets import (
    AssetRegisterItem, AssetRegisterReport, AssetsByConditionItem,
)
from app.shared.pagination import compute_pages


class AssetsReportService:

    @staticmethod
    async def register(db, params, status=None, condition=None) -> AssetRegisterReport:
        items, total, total_cost, total_paid = await AssetsReportRepo.register(db, params, status, condition)
        return AssetRegisterReport(
            items=[AssetRegisterItem.model_validate(a) for a in items],
            total=total, page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
            total_cost=total_cost, total_paid=total_paid, outstanding=total_cost - total_paid,
        )

    @staticmethod
    async def by_condition(db):
        rows = await AssetsReportRepo.by_condition(db)
        return [AssetsByConditionItem(**r) for r in rows]
