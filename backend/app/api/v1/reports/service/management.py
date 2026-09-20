from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.api.v1.reports.repository.management import ManagementReportRepo
from app.api.v1.reports.schemas.management import (
    FarmManagementSummary, MonthlyManagementReport, MonthlyReportItem,
    CustomerListItem, CustomerSalesItem, CustomerOutstandingItem,
    SupplierListItem, SupplierPurchasesItem, SupplierOutstandingItem,
)
from app.shared.pagination import compute_pages


class ManagementReportService:

    @staticmethod
    async def farm_summary(db, date_from: str, date_to: str) -> FarmManagementSummary:
        data = await ManagementReportRepo.farm_summary(db, date_from, date_to)
        return FarmManagementSummary(**data)

    @staticmethod
    async def monthly_report(db, year: int) -> MonthlyManagementReport:
        rows = await ManagementReportRepo.yearly_report(db, year)
        return MonthlyManagementReport(year=year, items=[MonthlyReportItem(**r) for r in rows])

    @staticmethod
    async def customers_list(db, params):
        items, total = await ManagementReportRepo.customers_list(db, params)
        return {
            'items': [CustomerListItem.model_validate(c) for c in items],
            'total': total, 'page': params.page, 'limit': params.limit, 'pages': compute_pages(total, params.limit),
        }

    @staticmethod
    async def customers_sales(db, date_from=None, date_to=None):
        rows = await ManagementReportRepo.customers_sales(db, date_from, date_to)
        return [CustomerSalesItem(**r) for r in rows]

    @staticmethod
    async def customers_outstanding(db):
        rows = await ManagementReportRepo.customers_outstanding(db)
        return [CustomerOutstandingItem(**r) for r in rows]

    @staticmethod
    async def suppliers_list(db, params):
        items, total = await ManagementReportRepo.suppliers_list(db, params)
        return {
            'items': [SupplierListItem.model_validate(s) for s in items],
            'total': total, 'page': params.page, 'limit': params.limit, 'pages': compute_pages(total, params.limit),
        }

    @staticmethod
    async def suppliers_purchases(db, date_from=None, date_to=None):
        rows = await ManagementReportRepo.suppliers_purchases(db, date_from, date_to)
        return [SupplierPurchasesItem(**r) for r in rows]

    @staticmethod
    async def suppliers_outstanding(db):
        rows = await ManagementReportRepo.suppliers_outstanding(db)
        return [SupplierOutstandingItem(**r) for r in rows]
