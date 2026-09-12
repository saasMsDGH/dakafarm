import re
with open("backend/app/api/v1/pos/service/SaleService.py", "r") as f:
    code = f.read()

pattern = re.compile(r'        try:\n            await db\.commit\(\)\n            await db\.refresh\(created_payment\)\n        except Exception as e:\n            await db\.rollback\(\)\n            raise HTTPException\(status_code=500, detail="Transaction failed\."\)\n\n        return created_payment', re.DOTALL)

replacement = """        try:
            db.expunge(created_payment)
            await db.commit()
            # Fetch freshly
            from sqlalchemy.future import select
            res = await db.execute(select(Payment).where(Payment.id == created_payment.id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed.")"""

code = pattern.sub(replacement, code)
with open("backend/app/api/v1/pos/service/SaleService.py", "w") as f:
    f.write(code)
