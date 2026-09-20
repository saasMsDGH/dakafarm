import asyncio
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///backend/amas_farm.db")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        result = await session.execute(text("SELECT current_quantity FROM flocks"))
        flocks = result.fetchall()
        print("FLOCKS:", flocks)
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        print("TODAY IS:", today)
        result = await session.execute(text(f"SELECT sum(good_eggs) FROM production_records WHERE record_date = '{today}'"))
        eggs = result.fetchall()
        print("EGGS TODAY:", eggs)

asyncio.run(test())
