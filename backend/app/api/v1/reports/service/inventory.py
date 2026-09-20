from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.api.v1.reports.repository.inventory import InventoryReportRepo
from app.api.v1.reports.schemas.inventory import (
    CurrentStockItem, CurrentStockReport, StockMovementItem, StockMovementReport,
    LowStockItem, InventoryValuationItem, InventoryValuationReport,
)
from app.shared.pagination import PaginationParams, compute_pages


class InventoryReportService:

    @staticmethod
    async def current_stock(db, params, category_id=None) -> CurrentStockReport:
        rows, total = await InventoryReportRepo.current_stock(db, params, category_id)
        return CurrentStockReport(
            items=[CurrentStockItem(**r) for r in rows],
            total=total, page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def stock_movements(db, params, product_id=None, movement_type=None, date_from=None, date_to=None) -> StockMovementReport:
        rows, total = await InventoryReportRepo.stock_movements(db, params, product_id, movement_type, date_from, date_to)
        return StockMovementReport(
            items=[StockMovementItem(**r) for r in rows],
            total=total, page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def low_stock(db) -> list:
        rows = await InventoryReportRepo.low_stock(db)
        return [LowStockItem(**r) for r in rows]

    @staticmethod
    async def valuation(db) -> InventoryValuationReport:
        rows, total_val = await InventoryReportRepo.valuation(db)
        return InventoryValuationReport(
            items=[InventoryValuationItem(**r) for r in rows],
            total_value=total_val,
        )
