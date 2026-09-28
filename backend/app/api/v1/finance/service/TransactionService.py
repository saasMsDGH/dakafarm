"""
TransactionService — business logic for FinancialTransaction.

Business rules enforced here:
  1. The referenced FinancialAccount must exist.
  2. The account must be active (is_active=True).  An inactive account
     cannot receive new transactions — this prevents recording against
     closed/suspended accounts while preserving their history.
  3. amount > 0 and direction IN/OUT are validated by the Pydantic schema
     before the service is ever called.
  4. transaction_date defaults to now() at the DB level if not supplied.
     If the client supplies a date it is used as-is (supports back-dating).
  5. Transactions are created and returned; no update/delete is exposed.

Note on DB session:
  The repository owns the commit (matching every other module in this project).
  The service does not issue a separate commit — only validation queries.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.repository.TransactionRepo import TransactionRepo
from app.api.v1.finance.schemas.TransactionSchema import (
    FinancialTransactionCreate,
    FinancialTransactionListResponse,
)
from app.shared.pagination import PaginationParams, compute_pages


class TransactionService:

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _get_active_account(db: AsyncSession, account_id: int) -> FinancialAccount:
        """
        Fetch the account and enforce two rules:
          - Account must exist.
          - Account must be active.
        Raises HTTP 404 / 422 respectively if either rule is violated.
        """
        result = await db.execute(
            select(FinancialAccount).where(FinancialAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial Account with id {account_id} not found.",
            )

        if not account.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Financial Account '{account.name}' is inactive. "
                    "Transactions cannot be posted to an inactive account."
                ),
            )

        return account

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    async def create(
        db: AsyncSession,
        request: FinancialTransactionCreate,
        current_user_id: int,
    ) -> FinancialTransaction:
        # Rule 1 + 2: account must exist and be active
        await TransactionService._get_active_account(db, request.account_id)

        new_txn = FinancialTransaction(
            account_id=request.account_id,
            transaction_type=request.transaction_type.value,
            direction=request.direction.value,
            amount=request.amount,
            description=request.description,
            reference_number=request.reference_number,
            created_by=current_user_id,
        )

        # Only set transaction_date explicitly if the client supplied one;
        # otherwise the DB server_default (now()) applies.
        if request.transaction_date is not None:
            new_txn.transaction_date = request.transaction_date

        return await TransactionRepo.create(db, new_txn)

    @staticmethod
    async def get_transaction(
        db: AsyncSession, transaction_id: int
    ) -> FinancialTransaction:
        txn = await TransactionRepo.get_by_id(db, transaction_id)
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial Transaction with id {transaction_id} not found.",
            )
        return txn

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        params: PaginationParams,
        account_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> FinancialTransactionListResponse:
        transactions, total = await TransactionRepo.list_transactions(
            db,
            params,
            account_id=account_id,
            transaction_type=transaction_type,
            direction=direction,
            date_from=date_from,
            date_to=date_to,
        )
        return FinancialTransactionListResponse(
            items=transactions,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )
