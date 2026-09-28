import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.expense_payment import ExpensePayment
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.pos.repository.ExpenseRepo import ExpenseRepo
from app.api.v1.pos.repository.ExpensePaymentRepo import ExpensePaymentRepo
from app.api.v1.finance.repository.AccountRepo import AccountRepo
from app.api.v1.pos.schemas.ExpenseSchema import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseUpdate,
)
from app.api.v1.pos.schemas.ExpensePaymentSchema import ExpensePaymentCreate
from app.shared.pagination import PaginationParams, compute_pages

class ExpenseService:
    @staticmethod
    def _generate_expense_number() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"EXP-{unique_suffix}"

    @staticmethod
    def _generate_payment_reference() -> str:
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"EXPPAY-{unique_suffix}"

    @staticmethod
    async def create(db: AsyncSession, request: ExpenseCreate, current_user_id: int) -> Expense:
        if request.amount_paid > request.amount:
            raise HTTPException(status_code=400, detail="Amount paid cannot exceed expense amount.")

        if request.amount_paid > 0:
            if not request.account_id:
                raise HTTPException(status_code=400, detail="account_id is required if amount_paid > 0")
            if not request.payment_method:
                raise HTTPException(status_code=400, detail="payment_method is required if amount_paid > 0")
            
            # Verify account exists
            account = await AccountRepo.get_by_id(db, request.account_id)
            if not account:
                raise HTTPException(status_code=404, detail="Financial account not found.")

        # Determine payment status
        if request.amount_paid == request.amount:
            payment_status = "PAID"
        elif request.amount_paid > 0:
            payment_status = "PARTIAL"
        else:
            payment_status = "UNPAID"

        expense_number = ExpenseService._generate_expense_number()

        new_expense = Expense(
            expense_number=expense_number,
            category=request.category,
            description=request.description,
            amount=request.amount,
            amount_paid=request.amount_paid,
            payment_status=payment_status,
            expense_date=request.expense_date,
            paid_by=current_user_id,
        )
        
        # We don't commit immediately so we can create payment atomically
        created_expense = await ExpenseRepo.create(db, new_expense, commit=False)

        if request.amount_paid > 0:
            # 1. Create ExpensePayment
            payment_ref = ExpenseService._generate_payment_reference()
            expense_payment = ExpensePayment(
                expense_id=created_expense.id,
                account_id=request.account_id,
                payment_reference=payment_ref,
                amount=request.amount_paid,
                payment_method=request.payment_method,
                paid_by=current_user_id
            )
            await ExpensePaymentRepo.create(db, expense_payment)

            # 2. Create FinancialTransaction
            fin_txn = FinancialTransaction(
                account_id=request.account_id,
                transaction_type="EXPENSE",
                direction="OUT",
                amount=request.amount_paid,
                description=f"Payment for Expense {expense_number} - {request.category}",
                reference_number=payment_ref,
                created_by=current_user_id
            )
            db.add(fin_txn)

        try:
            expense_id = created_expense.id
            await db.commit()
            return await ExpenseRepo.get_by_id(db, expense_id)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

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
            
        if expense.amount_paid > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete an expense that has payments recorded. This breaks the financial audit trail."
            )
            
        await ExpenseRepo.delete(db, expense)

    @staticmethod
    async def add_payment(db: AsyncSession, expense_id: int, request: ExpensePaymentCreate, current_user_id: int) -> ExpensePayment:
        expense = await ExpenseRepo.get_by_id(db, expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found.")

        if expense.payment_status == "PAID":
            raise HTTPException(status_code=400, detail="Expense is already fully paid.")

        remaining = expense.amount - expense.amount_paid
        if request.amount > remaining:
            raise HTTPException(status_code=400, detail=f"Payment amount exceeds remaining balance of {remaining}.")

        # Verify account
        account = await AccountRepo.get_by_id(db, request.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Financial account not found.")

        payment_ref = ExpenseService._generate_payment_reference()

        # 1. Create ExpensePayment
        payment = ExpensePayment(
            expense_id=expense.id,
            account_id=request.account_id,
            payment_reference=payment_ref,
            amount=request.amount,
            payment_method=request.payment_method,
            paid_by=current_user_id
        )
        await ExpensePaymentRepo.create(db, payment)

        # 2. Update Expense
        expense.amount_paid += request.amount
        if expense.amount_paid >= expense.amount:
            expense.payment_status = "PAID"
        else:
            expense.payment_status = "PARTIAL"

        # 3. Create FinancialTransaction
        fin_txn = FinancialTransaction(
            account_id=request.account_id,
            transaction_type="EXPENSE",
            direction="OUT",
            amount=request.amount,
            description=f"Payment for Expense {expense.expense_number} - {expense.category}",
            reference_number=payment_ref,
            created_by=current_user_id
        )
        db.add(fin_txn)

        try:
            await db.flush()
            payment_id = payment.id
            await db.commit()
            res = await db.execute(select(ExpensePayment).where(ExpensePayment.id == payment_id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

    @staticmethod
    async def get_payments_for_expense(db: AsyncSession, expense_id: int) -> list[ExpensePayment]:
        return await ExpensePaymentRepo.list_payments_for_expense(db, expense_id)
