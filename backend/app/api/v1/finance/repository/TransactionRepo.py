"""
TransactionRepo — database access for FinancialTransaction.

Immutability design:
  - There is no `update` or `delete` method.
  - Any future correction will go through a separate Reversal mechanism
    (Phase 2+) rather than mutating existing rows.

Filtering supported:
  - account_id, transaction_type, direction — exact match
  - date_from / date_to — inclusive date range on transaction_date
  - search — ilike on description OR reference_number

Sorting uses getattr on the model, falling back to created_at if the column
name is invalid — matching the pattern used in AccountRepo and AssetRepo.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.finance.models.transaction import FinancialTransaction
from app.shared.pagination import PaginationParams


class TransactionRepo:

    @staticmethod
    async def create(
        db: AsyncSession, transaction: FinancialTransaction
    ) -> FinancialTransaction:
        try:
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not save transaction due to a data integrity error.",
            )
        return transaction

    @staticmethod
    async def get_by_id(
        db: AsyncSession, transaction_id: int
    ) -> Optional[FinancialTransaction]:
        result = await db.execute(
            select(FinancialTransaction).where(FinancialTransaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        params: PaginationParams,
        account_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[FinancialTransaction], int]:
        query = select(FinancialTransaction)

        # --- Filters ---
        if account_id is not None:
            query = query.where(FinancialTransaction.account_id == account_id)

        if transaction_type:
            query = query.where(FinancialTransaction.transaction_type == transaction_type)

        if direction:
            query = query.where(FinancialTransaction.direction == direction)

        if date_from:
            query = query.where(FinancialTransaction.transaction_date >= date_from)

        if date_to:
            query = query.where(FinancialTransaction.transaction_date <= date_to)

        # --- Free-text search ---
        if params.search:
            term = f"%{params.search}%"
            query = query.where(
                or_(
                    FinancialTransaction.description.ilike(term),
                    FinancialTransaction.reference_number.ilike(term),
                )
            )

        # --- Count BEFORE pagination ---
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # --- Sorting (safe fallback to created_at) ---
        sort_column = getattr(
            FinancialTransaction, params.sort_by, FinancialTransaction.created_at
        )
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # --- Pagination ---
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        transactions = list(result.scalars().all())

        return transactions, total
