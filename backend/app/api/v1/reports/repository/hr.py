from __future__ import annotations
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.models.payroll import Payroll
from app.shared.pagination import PaginationParams


class HRReportRepo:

    @staticmethod
    async def employees(db, params):
        q = select(Employee)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(
                Employee.first_name.ilike(term) | Employee.last_name.ilike(term) | Employee.employee_code.ilike(term)
            )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(Employee.first_name.asc()).offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())
        return items, total

    @staticmethod
    async def payroll_summary(db, date_from=None, date_to=None):
        q = (
            select(
                Payroll.pay_period,
                func.count(Payroll.id).label('num_employees'),
                func.coalesce(func.sum(Payroll.basic_salary), 0).label('total_basic'),
                func.coalesce(func.sum(Payroll.allowances), 0).label('total_allowances'),
                func.coalesce(func.sum(Payroll.deductions), 0).label('total_deductions'),
                func.coalesce(func.sum(Payroll.net_salary), 0).label('total_net'),
                func.coalesce(func.sum(Payroll.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Payroll.net_salary - Payroll.amount_paid), 0).label('outstanding'),
            )
        )
        if date_from: q = q.where(Payroll.payment_date >= date_from)
        if date_to: q = q.where(Payroll.payment_date <= date_to)
        q = q.group_by(Payroll.pay_period).order_by(Payroll.pay_period.asc())
        rows = (await db.execute(q)).all()
        return [{'pay_period': r.pay_period, 'num_employees': r.num_employees,
                 'total_basic': Decimal(r.total_basic or 0), 'total_allowances': Decimal(r.total_allowances or 0),
                 'total_deductions': Decimal(r.total_deductions or 0), 'total_net': Decimal(r.total_net or 0),
                 'amount_paid': Decimal(r.amount_paid or 0), 'outstanding': Decimal(r.outstanding or 0)} for r in rows]

    @staticmethod
    async def payroll_detail(db, params, pay_period=None, employee_id=None):
        q = select(Payroll, Employee.first_name, Employee.last_name, Employee.employee_code).join(
            Employee, Payroll.employee_id == Employee.id
        )
        if pay_period: q = q.where(Payroll.pay_period == pay_period)
        if employee_id: q = q.where(Payroll.employee_id == employee_id)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Employee.first_name.ilike(term) | Employee.last_name.ilike(term))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(Payroll.pay_period.asc()).offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        items = [{'id': r[0].id, 'employee_name': f'{r[1]} {r[2]}', 'employee_code': r[3],
                  'pay_period': r[0].pay_period, 'basic_salary': Decimal(r[0].basic_salary or 0),
                  'allowances': Decimal(r[0].allowances or 0), 'deductions': Decimal(r[0].deductions or 0),
                  'net_salary': Decimal(r[0].net_salary or 0), 'amount_paid': Decimal(r[0].amount_paid or 0),
                  'outstanding': Decimal(r[0].net_salary or 0) - Decimal(r[0].amount_paid or 0),
                  'payment_date': r[0].payment_date, 'payment_status': r[0].payment_status} for r in rows]
        return items, total
