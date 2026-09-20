from __future__ import annotations
from decimal import Decimal

from app.api.v1.reports.repository.expenses import ExpensesReportRepo
from app.api.v1.reports.schemas.expenses import (
    ExpensesSummary, ExpensesDetailReport, ExpensesDetailItem, ExpensesByCategoryItem,
)
from app.shared.pagination import compute_pages


class ExpensesReportService:

    @staticmethod
    async def get_summary(db, date_from=None, date_to=None, category=None, payment_status=None):
        data = await ExpensesReportRepo.get_summary(db, date_from, date_to, category, payment_status)
        return ExpensesSummary(**data)

    @staticmethod
    async def get_detail(db, params, date_from=None, date_to=None, category=None, payment_status=None):
        items, total = await ExpensesReportRepo.list_detail(db, params, date_from, date_to, category, payment_status)
        summary_data = await ExpensesReportRepo.get_summary(db, date_from, date_to, category, payment_status)
        detail_items = [
            ExpensesDetailItem(
                id=e.id, expense_number=e.expense_number, expense_date=e.expense_date,
                category=e.category, description=e.description, amount=Decimal(e.amount),
                amount_paid=Decimal(e.amount_paid),
                outstanding=Decimal(e.amount) - Decimal(e.amount_paid),
                payment_status=e.payment_status,
                payment_method=getattr(e, 'payment_method', None),
                paid_by=e.paid_by,
            ) for e in items
        ]
        return ExpensesDetailReport(
            items=detail_items, total=total, page=params.page, limit=params.limit,
            pages=compute_pages(total, params.limit), summary=ExpensesSummary(**summary_data),
        )

    @staticmethod
    async def by_category(db, date_from=None, date_to=None):
        rows = await ExpensesReportRepo.by_category(db, date_from, date_to)
        return [ExpensesByCategoryItem(**r) for r in rows]
