from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.repository.BookRepo import BookRepo
from app.api.v1.reports.repository.financial import FinancialReportRepo
from app.api.v1.reports.schemas.financial import (
    CashBookReport, CashBookEntry, FinancialTransactionReport,
    FinancialTransactionReportItem, AccountSummaryReport, AccountSummaryItem,
    DailyFinancialSummary,
)
from app.api.v1.finance.models.account import FinancialAccount
from app.shared.pagination import PaginationParams, compute_pages
from decimal import Decimal
from sqlalchemy.future import select


class FinancialReportService:

    @staticmethod
    async def get_book_report(
        db: AsyncSession,
        account_id: int,
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> CashBookReport:
        # Fetch account info
        acc_result = await db.execute(select(FinancialAccount).where(FinancialAccount.id == account_id))
        account = acc_result.scalar_one_or_none()
        if not account:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Account not found")

        opening_balance = await BookRepo.get_opening_balance(db, account_id, date_from)
        txns, total, gap_sum = await BookRepo.list_transactions(
            db, account_id, params,
            date_from=date_from, date_to=date_to,
            transaction_type=transaction_type, direction=direction,
        )

        running = opening_balance + gap_sum
        total_in = Decimal(0)
        total_out = Decimal(0)
        entries = []
        for txn in txns:
            amt = Decimal(txn.amount)
            if txn.direction == 'IN':
                running += amt
                total_in += amt
            else:
                running -= amt
                total_out += amt
            entries.append(CashBookEntry(
                id=txn.id,
                transaction_date=txn.transaction_date,
                reference_number=txn.reference_number,
                description=txn.description,
                transaction_type=txn.transaction_type,
                direction=txn.direction,
                amount=amt,
                money_in=amt if txn.direction == 'IN' else None,
                money_out=amt if txn.direction == 'OUT' else None,
                running_balance=running,
            ))

        closing_balance = opening_balance + total_in - total_out

        return CashBookReport(
            account_id=account.id,
            account_name=account.name,
            account_type=account.account_type,
            opening_balance=opening_balance,
            total_in=total_in,
            total_out=total_out,
            closing_balance=closing_balance,
            items=entries,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def get_transaction_report(
        db: AsyncSession,
        params: PaginationParams,
        account_id: Optional[int] = None,
        account_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> FinancialTransactionReport:
        items, total, total_in, total_out = await FinancialReportRepo.list_transactions(
            db, params, account_id=account_id, account_type=account_type,
            transaction_type=transaction_type, direction=direction,
            date_from=date_from, date_to=date_to,
        )
        report_items = [
            FinancialTransactionReportItem(
                id=t.id,
                transaction_date=t.transaction_date,
                reference_number=t.reference_number,
                description=t.description,
                transaction_type=t.transaction_type,
                account_id=t.account_id,
                account_name=t.account.name if t.account else None,
                account_type=t.account.account_type if t.account else None,
                direction=t.direction,
                amount=Decimal(t.amount),
                created_by=t.created_by,
                created_at=t.created_at,
            )
            for t in items
        ]
        return FinancialTransactionReport(
            items=report_items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
            total_in=total_in,
            total_out=total_out,
            net=total_in - total_out,
        )

    @staticmethod
    async def get_account_summary(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        account_type: Optional[str] = None,
    ) -> AccountSummaryReport:
        rows = await FinancialReportRepo.get_account_summary(db, date_from, date_to, account_type)
        items = [AccountSummaryItem(**r) for r in rows]
        grand_in = sum(r.total_in for r in items)
        grand_out = sum(r.total_out for r in items)
        return AccountSummaryReport(
            items=items,
            grand_total_in=grand_in,
            grand_total_out=grand_out,
            grand_net=grand_in - grand_out,
        )

    @staticmethod
    async def get_daily_summary(db: AsyncSession, target_date: str) -> DailyFinancialSummary:
        data = await FinancialReportRepo.get_daily_summary(db, target_date)
        return DailyFinancialSummary(**data)
