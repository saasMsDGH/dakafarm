import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.api.v1.assets.schemas.AssetSchema import AssetCreate
from app.api.v1.assets.schemas.AssetPaymentSchema import AssetPaymentCreate
from app.api.v1.assets.service.AssetService import AssetService
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

        print("Creating Asset...")
        req = AssetCreate(
            name="Tractor",
            description="Big Tractor",
            purchase_date=date.today(),
            cost_price=Decimal('5000.00'),
            quantity=1,
            condition="New",
            amount_paid=Decimal('2000.00'),
            payment_method="CASH",
            account_id=acc_id
        )
        asset = await AssetService.create(db, req, usr_id)
        print(f"Created Asset: {asset.id}, code: {asset.asset_code}, total_cost: {asset.cost_price * asset.quantity}, paid: {asset.amount_paid}, status: {asset.payment_status}")
        
        print("Adding payment...")
        pay_req = AssetPaymentCreate(
            amount=Decimal('3000.00'),
            payment_method="BANK TRANSFER",
            account_id=acc_id
        )
        payment = await AssetService.add_payment(db, asset.id, pay_req, usr_id)
        print(f"Added payment. reference: {payment.payment_reference}")
        
        asset = await AssetService.get_asset(db, asset.id)
        print(f"Updated Asset status: {asset.payment_status}, paid: {asset.amount_paid}")

asyncio.run(run_test())
