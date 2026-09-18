from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.finance.models.account import FinancialAccount
from app.shared.pagination import PaginationParams

class AccountRepo:
    @staticmethod
    async def create(db: AsyncSession, account: FinancialAccount) -> FinancialAccount:
        try:
            db.add(account)
            await db.commit()
            await db.refresh(account)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this name might already exist."
            )
        return account

    @staticmethod
    async def get_by_id(db: AsyncSession, account_id: int) -> Optional[FinancialAccount]:
        result = await db.execute(select(FinancialAccount).where(FinancialAccount.id == account_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_accounts(db: AsyncSession, params: PaginationParams, account_type: str = None) -> Tuple[List[FinancialAccount], int]:
        query = select(FinancialAccount)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    FinancialAccount.name.ilike(search_term),
                    FinancialAccount.bank_name.ilike(search_term),
                    FinancialAccount.account_number.ilike(search_term)
                )
            )
        
        if account_type:
            query = query.where(FinancialAccount.account_type == account_type)

        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        sort_column = getattr(FinancialAccount, params.sort_by, FinancialAccount.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        accounts = list(result.scalars().all())

        return accounts, total

    @staticmethod
    async def update(db: AsyncSession, account: FinancialAccount, data: dict) -> FinancialAccount:
        for field, value in data.items():
            if value is not None:
                setattr(account, field, value)
        try:
            await db.commit()
            await db.refresh(account)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error updating account."
            )
        return account
