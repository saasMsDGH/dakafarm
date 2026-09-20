from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.repository.sales import SalesReportRepo
from app.api.v1.reports.schemas.sales import (
    SalesSummary, SalesDetailReport, SalesDetailItem,
    SalesByProductReport, SalesByProductItem, SalesByCustomerReport, SalesByCustomerItem,
    SalesByCategoryReport, SalesByCategoryItem, SalesPaymentStatusReport, SalesPaymentStatusItem,
)
from app.shared.pagination import PaginationParams, compute_pages


class SalesReportService:

    @staticmethod
    async def get_summary(db, date_from=None, date_to=None, customer_id=None, payment_status=None) -> SalesSummary:
        data = await SalesReportRepo.get_summary(db, date_from, date_to, customer_id, payment_status)
        return SalesSummary(**data)

    @staticmethod
    async def get_detail(db, params, date_from=None, date_to=None, customer_id=None, payment_status=None) -> SalesDetailReport:
        items, total = await SalesReportRepo.list_detail(db, params, date_from, date_to, customer_id, payment_status)
        summary_data = await SalesReportRepo.get_summary(db, date_from, date_to, customer_id, payment_status)
        detail_items = [
            SalesDetailItem(
                id=s.id, invoice_number=s.invoice_number, sale_date=s.sale_date,
                customer_name=s.customer.name if s.customer else None,
                subtotal=Decimal(s.subtotal), discount=Decimal(s.discount),
                total_amount=Decimal(s.total_amount), amount_paid=Decimal(s.amount_paid),
                outstanding=Decimal(s.total_amount) - Decimal(s.amount_paid),
                payment_status=s.payment_status, created_by=s.created_by,
            ) for s in items
        ]
        return SalesDetailReport(
            items=detail_items, total=total, page=params.page, limit=params.limit,
            pages=compute_pages(total, params.limit), summary=SalesSummary(**summary_data),
        )

    @staticmethod
    async def by_product(db, date_from=None, date_to=None) -> SalesByProductReport:
        rows = await SalesReportRepo.by_product(db, date_from, date_to)
        items = [SalesByProductItem(**r) for r in rows]
        total_rev = sum(i.revenue for i in items)
        return SalesByProductReport(items=items, total_revenue=total_rev)

    @staticmethod
    async def by_customer(db, date_from=None, date_to=None) -> SalesByCustomerReport:
        rows = await SalesReportRepo.by_customer(db, date_from, date_to)
        return SalesByCustomerReport(items=[SalesByCustomerItem(**r) for r in rows])

    @staticmethod
    async def by_category(db, date_from=None, date_to=None) -> SalesByCategoryReport:
        rows, total_rev = await SalesReportRepo.by_category(db, date_from, date_to)
        return SalesByCategoryReport(items=[SalesByCategoryItem(**r) for r in rows], total_revenue=total_rev)

    @staticmethod
    async def payment_status(db, date_from=None, date_to=None) -> SalesPaymentStatusReport:
        rows = await SalesReportRepo.payment_status_breakdown(db, date_from, date_to)
        return SalesPaymentStatusReport(items=[SalesPaymentStatusItem(**r) for r in rows])
