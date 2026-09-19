import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.api.v1.hr.schemas.PayrollSchema import PayrollCreate
from app.api.v1.hr.schemas.PayrollPaymentSchema import PayrollPaymentCreate
from app.api.v1.hr.service.PayrollService import PayrollService
from app.api.v1.finance.repository.AccountRepo import AccountRepo
from app.api.v1.finance.models.account import FinancialAccount
from decimal import Decimal
from datetime import date
import app.db

engine = create_async_engine("postgresql+asyncpg://postgres:first_password123@db:5432/msa_db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def run_test():
    async with AsyncSessionLocal() as db:
        print("Ensuring dummy user exists...")
        usr = await db.execute(text("SELECT id FROM users LIMIT 1"))
        usr_row = usr.fetchone()
        
        if not usr_row:
            await db.execute(text("INSERT INTO users (id, first_name, last_name, email, password_hash) VALUES (1, 'Test', 'User', 'test@example.com', 'hash') ON CONFLICT (id) DO NOTHING"))
            await db.commit()
            usr_id = 1
        else:
            usr_id = usr_row[0]

        print("Ensuring dummy account exists...")
        acc = await db.execute(text("SELECT id FROM financial_accounts LIMIT 1"))
        acc_row = acc.fetchone()
        
        if not acc_row:
            dummy_acc = FinancialAccount(
                account_name="Test Account",
                account_type="CASH",
                balance=Decimal('10000.00'),
                currency="RWF",
                created_by=usr_id
            )
            db.add(dummy_acc)
            await db.commit()
            await db.refresh(dummy_acc)
            acc_id = dummy_acc.id
        else:
            acc_id = acc_row[0]

        print("Ensuring dummy employee exists...")
        emp = await db.execute(text("SELECT id FROM employees LIMIT 1"))
        emp_row = emp.fetchone()
        
        if not emp_row:
            await db.execute(text("INSERT INTO employees (first_name, last_name, position, department, hire_date, salary) VALUES ('Test', 'Emp', 'Worker', 'Farm', '2020-01-01', 500.00)"))
            await db.commit()
            emp = await db.execute(text("SELECT id FROM employees LIMIT 1"))
            emp_id = emp.fetchone()[0]
        else:
            emp_id = emp_row[0]

        print("Creating Payroll...")
        try:
            req = PayrollCreate(
                employee_id=emp_id,
                pay_period="2023-10",
                basic_salary=Decimal('500.00'),
                allowances=Decimal('50.00'),
                deductions=Decimal('10.00'),
                payment_date=date.today(),
                amount_paid=Decimal('200.00'),
                payment_method="CASH",
                account_id=acc_id
            )
            payroll = await PayrollService.create(db, req, usr_id)
            print(f"Created Payroll: {payroll.id}, net_salary: {payroll.net_salary}, paid: {payroll.amount_paid}, status: {payroll.payment_status}")
            
            print("Adding payment...")
            pay_req = PayrollPaymentCreate(
                amount=Decimal('340.00'),
                payment_method="BANK TRANSFER",
                account_id=acc_id
            )
            payment = await PayrollService.add_payment(db, payroll.id, pay_req, usr_id)
            print(f"Added payment. reference: {payment.payment_reference}")
            
            payroll = await PayrollService.get_payroll(db, payroll.id)
            print(f"Updated Payroll status: {payroll.payment_status}, paid: {payroll.amount_paid}")
            
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(run_test())
