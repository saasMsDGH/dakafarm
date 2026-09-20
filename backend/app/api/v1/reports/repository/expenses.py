from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.pos.models.expense import Expense
from app.shared.pagination import PaginationParams


class ExpensesReportRepo:

    @staticmethod
    async def get_summary(db, date_from=None, date_to=None, category=None, payment_status=None):
        q = select(
            func.count(Expense.id).label('total_expenses'),
            func.coalesce(func.sum(Expense.amount), 0).label('total_amount'),
            func.coalesce(func.sum(Expense.amount_paid), 0).label('amount_paid'),
            func.coalesce(func.sum(Expense.amount - Expense.amount_paid), 0).label('outstanding'),
        )
        if date_from: q = q.where(Expense.expense_date >= date_from)
        if date_to: q = q.where(Expense.expense_date <= date_to)
        if category: q = q.where(Expense.category.ilike(f'%{category}%'))
        if payment_status: q = q.where(Expense.payment_status == payment_status)
        r = (await db.execute(q)).one()
        return {'total_expenses': r.total_expenses or 0, 'total_amount': Decimal(r.total_amount or 0),
                'amount_paid': Decimal(r.amount_paid or 0), 'outstanding': Decimal(r.outstanding or 0)}

    @staticmethod
    async def list_detail(db, params, date_from=None, date_to=None, category=None, payment_status=None):
        q = select(Expense)
        if date_from: q = q.where(Expense.expense_date >= date_from)
        if date_to: q = q.where(Expense.expense_date <= date_to)
        if category: q = q.where(Expense.category.ilike(f'%{category}%'))
        if payment_status: q = q.where(Expense.payment_status == payment_status)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Expense.expense_number.ilike(term) | Expense.description.ilike(term))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        sort_col = getattr(Expense, params.sort_by, Expense.expense_date)
        q = q.order_by(sort_col.desc() if params.order == 'desc' else sort_col.asc())
        q = q.offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())
        return items, total

    @staticmethod
    async def by_category(db, date_from=None, date_to=None):
        q = (
            select(
                Expense.category,
                func.count(Expense.id).label('num_transactions'),
                func.coalesce(func.sum(Expense.amount), 0).label('total_amount'),
                func.coalesce(func.sum(Expense.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Expense.amount - Expense.amount_paid), 0).label('outstanding'),
            )
        )
        if date_from: q = q.where(Expense.expense_date >= date_from)
        if date_to: q = q.where(Expense.expense_date <= date_to)
        q = q.group_by(Expense.category)
        rows = (await db.execute(q)).all()
        grand_total = sum(Decimal(r.total_amount or 0) for r in rows)
        return [{
            'category': r.category,
            'num_transactions': r.num_transactions,
            'total_amount': Decimal(r.total_amount or 0),
            'amount_paid': Decimal(r.amount_paid or 0),
            'outstanding': Decimal(r.outstanding or 0),
            'percentage': (Decimal(r.total_amount or 0) / grand_total * 100).quantize(Decimal('0.01')) if grand_total > 0 else Decimal(0),
        } for r in rows]
