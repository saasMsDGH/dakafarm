from app.api.v1.user import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.future import select

class UserRepo:
    @staticmethod
    async def createUser(db: AsyncSession, user: models.Users):
        try:
            db.add(user)
            # Flush sends it to the DB to get an ID, but doesn't permanently commit yet
            await db.flush() 
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conflicts: data already exists"
            )
        return user

    @staticmethod
    async def get_role(db: AsyncSession, role_name: str):
        results = await db.execute(select(models.Roles).where(models.Roles.name == role_name))
        return results.scalar_one_or_none()

    @staticmethod
    async def create_role(db: AsyncSession, user_role: models.UserRole):
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)
        return user_role