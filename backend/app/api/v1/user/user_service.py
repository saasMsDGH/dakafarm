from app.api.v1.user.repository import UserRepo
from app.api.v1.user import schemas,models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status
from app.core.security import Hash





class UserService:
    @staticmethod
    async def CreateUser_service(
        request: schemas.User,
        db: AsyncSession,
    ):
        user = models.Users(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone=request.phone,
            password_hash=Hash.hash(request.password_hash),
        )

        user = await UserRepo.createUser(db, user)

        # Assign the requested role (defaults to "Farm Worker" if not specified)
        role = await UserRepo.get_role(db, request.role)
        if not role:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{request.role}' does not exist. Seed roles first via POST /db.",
            )

        user_role = models.UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)

        await db.commit()
        await db.refresh(user)

        return user