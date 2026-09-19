import asyncio
import os
import sys

# Add project root to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, func
from app.core.database import sessionlocal
from app.api.v1.finance.models.transaction import FinancialTransaction

async def main():
    import app.core.config
    app.core.config.settings.DATABASE_URL = app.core.config.settings.DATABASE_URL.replace("db", "localhost")
    from app.core.database import engine
    
    async with sessionlocal() as db:
        res = await db.execute(
            select(FinancialTransaction.transaction_type, FinancialTransaction.direction, func.sum(FinancialTransaction.amount))
            .group_by(FinancialTransaction.transaction_type, FinancialTransaction.direction)
        )
        for row in res.all():
            print(f"{row[0]} | {row[1]} | {row[2]}")

if __name__ == "__main__":
    asyncio.run(main())
