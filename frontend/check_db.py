import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://postgres:first_password123@localhost:5432/msa_db')
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT id, name, account_type, is_active FROM financial_accounts'))
        for row in result.fetchall():
            print(row)

asyncio.run(main())
