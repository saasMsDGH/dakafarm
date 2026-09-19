import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///backend/amas_farm.db")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        result = await session.execute(text("SELECT * FROM flocks"))
        print("FLOCKS:", result.fetchall())
        
        result = await session.execute(text("SELECT * FROM production_records"))
        print("EGGS:", result.fetchall())

asyncio.run(test())
