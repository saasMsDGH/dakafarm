from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.farm.models import house
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError




class HouseRepo:
    @staticmethod
    async def create_house(db:AsyncSession,house:house.House):
        try:
            db.add(house)
            await db.commit()
            await db.refresh(house)
        except  IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail="conflicts: IntegrityError"
            )

        return house