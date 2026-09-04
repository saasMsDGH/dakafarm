
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings




SQL_DATABASE_URL = (settings.DATABASE_URL)


engine = create_async_engine(SQL_DATABASE_URL)

sessionlocal = sessionmaker(
        class_= AsyncSession,
        autocommit=False,
        autoflush=False,
        bind=engine
    )


Base = declarative_base()

async def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
       await db.close()


