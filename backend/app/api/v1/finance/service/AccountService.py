from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.repository.AccountRepo import AccountRepo
from app.api.v1.finance.schemas.AccountSchema import (
    FinancialAccountCreate,
    FinancialAccountListResponse,
    FinancialAccountUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class AccountService:
    @staticmethod
    async def create(db: AsyncSession, request: FinancialAccountCreate, current_user_id: int) -> FinancialAccount:
        new_account = FinancialAccount(
            name=request.name,
            account_type=request.account_type,
            bank_name=request.bank_name,
            account_number=request.account_number,
            opening_balance=request.opening_balance,
            is_active=request.is_active,
            created_by=current_user_id
        )
        return await AccountRepo.create(db, new_account)

    @staticmethod
    async def get_account(db: AsyncSession, account_id: int) -> FinancialAccount:
        account = await AccountRepo.get_by_id(db, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial Account with id {account_id} not found."
            )
        return account

    @staticmethod
    async def list_accounts(db: AsyncSession, params: PaginationParams, account_type: str = None) -> FinancialAccountListResponse:
        accounts, total = await AccountRepo.list_accounts(db, params, account_type)
        return FinancialAccountListResponse(
            items=accounts,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )

    @staticmethod
    async def update(db: AsyncSession, account_id: int, request: FinancialAccountUpdate) -> FinancialAccount:
        account = await AccountRepo.get_by_id(db, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial Account with id {account_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await AccountRepo.update(db, account, update_data)
