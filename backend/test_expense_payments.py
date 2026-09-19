import asyncio
import uuid
from decimal import Decimal
from sqlalchemy.future import select
from app.core.database import sessionlocal
import app.db
from app.api.v1.pos.service.ExpenseService import ExpenseService
from app.api.v1.pos.schemas.ExpenseSchema import ExpenseCreate
from app.api.v1.pos.schemas.ExpensePaymentSchema import ExpensePaymentCreate
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.user.models import Users

async def main():
    async with sessionlocal() as db:
        try:
            acc = FinancialAccount(name=f"Acc-{uuid.uuid4().hex[:6]}", account_type="CASH", opening_balance=1000)
            db.add(acc)
            await db.flush()
            acc_id = acc.id

            create_req = ExpenseCreate(
                category="Test",
                description="Test",
                amount=Decimal('500.00'),
                amount_paid=Decimal('0.00'),
                payment_method=None,
                account_id=None
            )
            expense = await ExpenseService.create(db, create_req, None)
            print(f"Created Expense: {expense.amount_paid}, {expense.payment_status}")
            assert expense.payment_status == "UNPAID"

            expense_id = expense.id
            pay_req = ExpensePaymentCreate(amount=Decimal('200.00'), payment_method="CASH", account_id=acc_id)
            payment = await ExpenseService.add_payment(db, expense_id, pay_req, None)
            
            expense_after_partial = await ExpenseService.get_expense(db, expense_id)
            print(f"After Partial: {expense_after_partial.amount_paid}, {expense_after_partial.payment_status}")
            assert expense_after_partial.payment_status == "PARTIAL"

            txns = (await db.execute(select(FinancialTransaction).where(FinancialTransaction.reference_number == payment.payment_reference))).scalars().all()
            print(f"Financial Txns created: {len(txns)}")
            assert len(txns) == 1

            pay_req_2 = ExpensePaymentCreate(amount=Decimal('300.00'), payment_method="CASH", account_id=acc_id)
            payment_2 = await ExpenseService.add_payment(db, expense_id, pay_req_2, None)

            expense_after_full = await ExpenseService.get_expense(db, expense_id)
            print(f"After Full: {expense_after_full.amount_paid}, {expense_after_full.payment_status}")
            assert expense_after_full.payment_status == "PAID"

            print("SUCCESS")
            
        except Exception as e:
            print(f"ERROR: {e}")
            raise e
        finally:
            await db.rollback()

if __name__ == '__main__':
    asyncio.run(main())
