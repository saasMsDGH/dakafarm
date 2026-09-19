import asyncio
from app.core.database import SessionLocal
from sqlalchemy import text

async def check():
    async with SessionLocal() as db:
        res1 = await db.execute(text("SELECT SUM(total_amount), SUM(amount_paid) FROM sales"))
        s_tot, s_paid = res1.fetchone()
        res2 = await db.execute(text("SELECT SUM(total_amount), SUM(amount_paid) FROM purchases"))
        p_tot, p_paid = res2.fetchone()
        res3 = await db.execute(text("SELECT SUM(amount) FROM financial_transactions WHERE transaction_type='SALE' AND direction='IN'"))
        s_in = res3.scalar()
        res4 = await db.execute(text("SELECT SUM(amount) FROM financial_transactions WHERE transaction_type='PURCHASE' AND direction='OUT'"))
        p_out = res4.scalar()
        print(f"Sales: total={s_tot}, paid={s_paid}, flow_in={s_in}")
        print(f"Purchs: total={p_tot}, paid={p_paid}, flow_out={p_out}")

asyncio.run(check())
