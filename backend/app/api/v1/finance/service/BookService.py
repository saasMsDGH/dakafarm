from typing import Optional
from decimal import Decimal
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.repository.BookRepo import BookRepo
from app.api.v1.finance.schemas.BookSchema import BookResponse, BookEntry, BookPagination
from app.shared.pagination import PaginationParams, compute_pages

class BookService:
    @staticmethod
    async def get_book(
        db: AsyncSession,
        expected_type: str,
        account_id: int,
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> BookResponse:
        
        # 1. Verify account and its type
        result = await db.execute(select(FinancialAccount).where(FinancialAccount.id == account_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial Account with id {account_id} not found."
            )
        if account.account_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account '{account.name}' is of type {account.account_type}, but {expected_type} book was requested."
            )

        # 2. Get period opening balance (account opening bal + (IN-OUT before date_from))
        period_opening_balance = await BookRepo.get_opening_balance(db, account_id, date_from)

        # 3. Get transactions and gap sum for pagination
        transactions, total, gap_sum = await BookRepo.list_transactions(
            db, account_id, params, date_from, date_to, transaction_type, direction
        )

        # 4. Calculate running balances
        items = []
        running_balance = period_opening_balance + gap_sum
        total_money_in = Decimal('0.00')
        total_money_out = Decimal('0.00')

        for tx in transactions:
            money_in = Decimal(tx.amount) if tx.direction == 'IN' else Decimal('0.00')
            money_out = Decimal(tx.amount) if tx.direction == 'OUT' else Decimal('0.00')
            
            total_money_in += money_in
            total_money_out += money_out
            
            running_balance += money_in
            running_balance -= money_out

            items.append(BookEntry(
                id=tx.id,
                transaction_date=tx.transaction_date,
                reference_number=tx.reference_number,
                description=tx.description,
                transaction_type=tx.transaction_type,
                money_in=money_in,
                money_out=money_out,
                balance=running_balance
            ))

        pagination = BookPagination(
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )

        return BookResponse(
            account=account,
            opening_balance=period_opening_balance + gap_sum,
            items=items,
            total_money_in=total_money_in,
            total_money_out=total_money_out,
            closing_balance=running_balance,
            pagination=pagination
        )
