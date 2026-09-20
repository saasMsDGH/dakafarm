from __future__ import annotations
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.reports.repository.purchases import PurchasesReportRepo
from app.api.v1.reports.schemas.purchases import (
    PurchasesSummary, PurchasesDetailReport, PurchasesDetailItem,
    PurchasesBySupplierItem, PurchasesByProductItem,
)
from app.shared.pagination import compute_pages


class PurchasesReportService:

    @staticmethod
    async def get_summary(db, date_from=None, date_to=None, supplier_id=None, payment_status=None):
        data = await PurchasesReportRepo.get_summary(db, date_from, date_to, supplier_id, payment_status)
        return PurchasesSummary(**data)

    @staticmethod
    async def get_detail(db, params, date_from=None, date_to=None, supplier_id=None, payment_status=None):
        items, total = await PurchasesReportRepo.list_detail(db, params, date_from, date_to, supplier_id, payment_status)
        summary_data = await PurchasesReportRepo.get_summary(db, date_from, date_to, supplier_id, payment_status)
        detail_items = [
            PurchasesDetailItem(
                id=p.id, purchase_number=p.purchase_number, purchase_date=p.purchase_date,
                supplier_name=p.supplier.name if p.supplier else None,
                subtotal=Decimal(p.subtotal), discount=Decimal(p.discount),
                total_amount=Decimal(p.total_amount), amount_paid=Decimal(p.amount_paid),
                outstanding=Decimal(p.total_amount) - Decimal(p.amount_paid),
                payment_status=p.payment_status, notes=getattr(p, 'notes', None),
            ) for p in items
        ]
        return PurchasesDetailReport(
            items=detail_items, total=total, page=params.page, limit=params.limit,
            pages=compute_pages(total, params.limit), summary=PurchasesSummary(**summary_data),
        )

    @staticmethod
    async def by_supplier(db, date_from=None, date_to=None):
        rows = await PurchasesReportRepo.by_supplier(db, date_from, date_to)
        return [PurchasesBySupplierItem(**r) for r in rows]

    @staticmethod
    async def by_product(db, date_from=None, date_to=None):
        rows = await PurchasesReportRepo.by_product(db, date_from, date_to)
        return [PurchasesByProductItem(**r) for r in rows]
