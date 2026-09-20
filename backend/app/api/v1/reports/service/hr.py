from __future__ import annotations
from decimal import Decimal

from app.api.v1.reports.repository.hr import HRReportRepo
from app.api.v1.reports.schemas.hr import (
    EmployeeReportItem, EmployeeReport, PayrollSummaryReport, PayrollSummaryByPeriod,
    PayrollDetailReport, PayrollDetailItem,
)
from app.shared.pagination import compute_pages


class HRReportService:

    @staticmethod
    async def employees(db, params) -> EmployeeReport:
        items, total = await HRReportRepo.employees(db, params)
        return EmployeeReport(
            items=[EmployeeReportItem.model_validate(e) for e in items],
            total=total, page=params.page, limit=params.limit, pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def payroll_summary(db, date_from=None, date_to=None) -> PayrollSummaryReport:
        rows = await HRReportRepo.payroll_summary(db, date_from, date_to)
        items = [PayrollSummaryByPeriod(**r) for r in rows]
        return PayrollSummaryReport(
            items=items,
            grand_total_net=sum(i.total_net for i in items),
            grand_amount_paid=sum(i.amount_paid for i in items),
            grand_outstanding=sum(i.outstanding for i in items),
        )

    @staticmethod
    async def payroll_detail(db, params, pay_period=None, employee_id=None) -> PayrollDetailReport:
        rows, total = await HRReportRepo.payroll_detail(db, params, pay_period, employee_id)
        items = [PayrollDetailItem(**r) for r in rows]
        totals = PayrollSummaryByPeriod(
            pay_period=pay_period or 'All', num_employees=total,
            total_basic=sum(i.basic_salary for i in items),
            total_allowances=sum(i.allowances for i in items),
            total_deductions=sum(i.deductions for i in items),
            total_net=sum(i.net_salary for i in items),
            amount_paid=sum(i.amount_paid for i in items),
            outstanding=sum(i.outstanding for i in items),
        )
        return PayrollDetailReport(
            items=items, total=total, page=params.page, limit=params.limit,
            pages=compute_pages(total, params.limit), summary=totals,
        )
