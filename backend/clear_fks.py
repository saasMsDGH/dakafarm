import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:first_password123@db:5432/msa_db"

async def clear_fks():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE feed_records SET product_id = NULL"))
        await conn.execute(text("UPDATE medication_records SET product_id = NULL"))
        await conn.execute(text("UPDATE vaccination_records SET product_id = NULL"))
    print("FKs cleared")

asyncio.run(clear_fks())
