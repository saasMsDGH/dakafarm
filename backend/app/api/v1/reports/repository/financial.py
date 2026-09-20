from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import func, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.repository.BookRepo import BookRepo
from app.shared.pagination import PaginationParams, compute_pages


class FinancialReportRepo:

    @staticmethod
    async def get_account_summary(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        account_type: Optional[str] = None,
    ) -> list[dict]:
        q = select(FinancialAccount).where(FinancialAccount.is_active == True)
        if account_type:
            q = q.where(FinancialAccount.account_type == account_type)
        result = await db.execute(q)
        accounts = result.scalars().all()

        rows = []
        for acc in accounts:
            in_q = select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
                FinancialTransaction.account_id == acc.id,
                FinancialTransaction.direction == 'IN',
            )
            out_q = select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
                FinancialTransaction.account_id == acc.id,
                FinancialTransaction.direction == 'OUT',
            )
            if date_from:
                in_q = in_q.where(FinancialTransaction.transaction_date >= date_from)
                out_q = out_q.where(FinancialTransaction.transaction_date >= date_from)
            if date_to:
                in_q = in_q.where(FinancialTransaction.transaction_date <= date_to)
                out_q = out_q.where(FinancialTransaction.transaction_date <= date_to)

            total_in = Decimal((await db.execute(in_q)).scalar() or 0)
            total_out = Decimal((await db.execute(out_q)).scalar() or 0)
            opening_balance = await BookRepo.get_opening_balance(db, acc.id, date_from)

            rows.append({
                'account_id': acc.id,
                'account_name': acc.name,
                'account_type': acc.account_type,
                'opening_balance': opening_balance,
                'total_in': total_in,
                'total_out': total_out,
                'closing_balance': opening_balance + total_in - total_out,
            })
        return rows

    @staticmethod
    async def get_daily_summary(db: AsyncSession, target_date: str) -> dict:
        from datetime import datetime as dt
        day_start = dt.strptime(target_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        day_end = dt.strptime(target_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        accounts = (await db.execute(
            select(FinancialAccount).where(FinancialAccount.is_active == True)
        )).scalars().all()
        acc_by_type = {}
        for acc in accounts:
            acc_by_type.setdefault(acc.account_type, []).append(acc.id)

        async def sum_dir(direction, account_ids=None):
            q = select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
                FinancialTransaction.direction == direction,
                FinancialTransaction.transaction_date >= day_start,
                FinancialTransaction.transaction_date <= day_end,
            )
            if account_ids is not None:
                q = q.where(FinancialTransaction.account_id.in_(account_ids))
            return Decimal((await db.execute(q)).scalar() or 0)

        total_in = await sum_dir('IN')
        total_out = await sum_dir('OUT')
        cash_ids = acc_by_type.get('cash', [])
        bank_ids = acc_by_type.get('bank', [])
        mobile_ids = acc_by_type.get('mobile', [])

        return {
            'date': target_date,
            'total_in': total_in,
            'total_out': total_out,
            'net': total_in - total_out,
            'cash_in': await sum_dir('IN', cash_ids) if cash_ids else Decimal(0),
            'cash_out': await sum_dir('OUT', cash_ids) if cash_ids else Decimal(0),
            'bank_in': await sum_dir('IN', bank_ids) if bank_ids else Decimal(0),
            'bank_out': await sum_dir('OUT', bank_ids) if bank_ids else Decimal(0),
            'mobile_in': await sum_dir('IN', mobile_ids) if mobile_ids else Decimal(0),
            'mobile_out': await sum_dir('OUT', mobile_ids) if mobile_ids else Decimal(0),
        }

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        params: PaginationParams,
        account_id: Optional[int] = None,
        account_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ):
        q = select(FinancialTransaction).options(joinedload(FinancialTransaction.account))

        if account_id:
            q = q.where(FinancialTransaction.account_id == account_id)
        if account_type:
            from sqlalchemy.orm import join
            q = q.join(FinancialAccount, FinancialTransaction.account_id == FinancialAccount.id).where(
                FinancialAccount.account_type == account_type
            )
        if transaction_type:
            q = q.where(FinancialTransaction.transaction_type == transaction_type)
        if direction:
            q = q.where(FinancialTransaction.direction == direction)
        if date_from:
            q = q.where(FinancialTransaction.transaction_date >= date_from)
        if date_to:
            q = q.where(FinancialTransaction.transaction_date <= date_to)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(or_(
                FinancialTransaction.description.ilike(term),
                FinancialTransaction.reference_number.ilike(term),
            ))

        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0

        sort_col = getattr(FinancialTransaction, params.sort_by, FinancialTransaction.transaction_date)
        q = q.order_by(sort_col.desc() if params.order == 'desc' else sort_col.asc())
        q = q.offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())

        in_sum = Decimal(0)
        out_sum = Decimal(0)
        for it in items:
            if it.direction == 'IN':
                in_sum += Decimal(it.amount)
            else:
                out_sum += Decimal(it.amount)

        return items, total, in_sum, out_sum
