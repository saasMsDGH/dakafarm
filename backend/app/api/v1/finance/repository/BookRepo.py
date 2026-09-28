from typing import Tuple, List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.shared.pagination import PaginationParams

class BookRepo:
    @staticmethod
    async def get_opening_balance(
        db: AsyncSession,
        account_id: int,
        date_from: Optional[datetime] = None
    ) -> Decimal:
        """
        Calculate opening balance for a specific account up to date_from.
        Formula: Account.opening_balance + SUM(IN) - SUM(OUT) before date_from.
        """
        result = await db.execute(
            select(FinancialAccount.opening_balance)
            .where(FinancialAccount.id == account_id)
        )
        base_bal = result.scalar()
        if base_bal is None:
            return Decimal('0.00')

        if not date_from:
            return Decimal(base_bal)

        # Sum transactions before date_from
        from sqlalchemy import case
        query = (
            select(
                func.sum(
                    case(
                        (FinancialTransaction.direction == 'IN', FinancialTransaction.amount),
                        (FinancialTransaction.direction == 'OUT', -FinancialTransaction.amount),
                        else_=0
                    )
                )
            )
            .where(FinancialTransaction.account_id == account_id)
            .where(FinancialTransaction.transaction_date < date_from)
        )
        txn_result = await db.execute(query)
        txn_sum = txn_result.scalar() or Decimal('0.00')

        return Decimal(base_bal) + Decimal(txn_sum)

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        account_id: int,
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Tuple[List[FinancialTransaction], int, Decimal]:
        
        query = select(FinancialTransaction).where(FinancialTransaction.account_id == account_id)

        if date_from:
            query = query.where(FinancialTransaction.transaction_date >= date_from)
        if date_to:
            query = query.where(FinancialTransaction.transaction_date <= date_to)
        if transaction_type:
            query = query.where(FinancialTransaction.transaction_type == transaction_type)
        if direction:
            query = query.where(FinancialTransaction.direction == direction)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    FinancialTransaction.description.ilike(search_term),
                    FinancialTransaction.reference_number.ilike(search_term)
                )
            )

        # Get total count
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Deterministic ordering required for running balances
        query = query.order_by(FinancialTransaction.transaction_date.asc(), FinancialTransaction.id.asc())

        # Calculate gap_sum for pagination (sum of IN - OUT for items before the offset)
        gap_sum = Decimal('0.00')
        if params.offset > 0:
            gap_query = query.limit(params.offset)
            res = await db.execute(gap_query)
            gap_txns = res.scalars().all()
            for tx in gap_txns:
                if tx.direction == 'IN':
                    gap_sum += Decimal(tx.amount)
                elif tx.direction == 'OUT':
                    gap_sum -= Decimal(tx.amount)

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        transactions = list(result.scalars().all())

        return transactions, total, gap_sum
