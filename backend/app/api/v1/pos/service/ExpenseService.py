import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.repository.ExpenseRepo import ExpenseRepo
from app.api.v1.pos.schemas.ExpenseSchema import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseUpdate,
)
from app.shared.pagination import PaginationParams, compute_pages

class ExpenseService:
    @staticmethod
    def _generate_expense_number() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"EXP-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: ExpenseCreate, current_user_id: int) -> Expense:
        expense_number = ExpenseService._generate_expense_number()

        new_expense = Expense(
            expense_number=expense_number,
            category=request.category,
            description=request.description,
            amount=request.amount,
            expense_date=request.expense_date,
            payment_method=request.payment_method,
            paid_by=current_user_id,
        )
        return await ExpenseRepo.create(db, new_expense)

    @staticmethod
    async def get_expense(db: AsyncSession, expense_id: int) -> Expense:
        expense = await ExpenseRepo.get_by_id(db, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with id {expense_id} not found."
            )
        return expense

    @staticmethod
    async def list_expenses(db: AsyncSession, params: PaginationParams, category: str = None) -> ExpenseListResponse:
        expenses, total = await ExpenseRepo.list_expenses(db, params, category)
        return ExpenseListResponse(
            items=expenses,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit),
        )

    @staticmethod
    async def update(db: AsyncSession, expense_id: int, request: ExpenseUpdate) -> Expense:
        expense = await ExpenseRepo.get_by_id(db, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with id {expense_id} not found."
            )
        update_data = request.model_dump(exclude_unset=True)
        return await ExpenseRepo.update(db, expense, update_data)

    @staticmethod
    async def delete(db: AsyncSession, expense_id: int) -> None:
        expense = await ExpenseRepo.get_by_id(db, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with id {expense_id} not found."
            )
        await ExpenseRepo.delete(db, expense)
