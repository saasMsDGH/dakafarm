from typing import Optional, Tuple, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.api.v1.user import models
from app.shared.pagination import PaginationParams


class UserRepo:
    @staticmethod
    async def createUser(db: AsyncSession, user: models.Users):
        try:
            db.add(user)
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

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[models.Users]:
        result = await db.execute(
            select(models.Users)
            .options(
                selectinload(models.Users.role)
                .selectinload(models.UserRole.roleid)
            )
            .where(models.Users.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        params: PaginationParams
    ) -> Tuple[List[models.Users], int]:
        query = select(models.Users).options(
            selectinload(models.Users.role)
            .selectinload(models.UserRole.roleid)
        )
        
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Sort
        sort_column = getattr(models.Users, params.sort_by, models.Users.created_at)
        if params.order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Paginate
        query = query.offset(params.offset).limit(params.limit)
        result = await db.execute(query)
        users = list(result.scalars().all())

        return users, total

    @staticmethod
    async def update_user(db: AsyncSession, user: models.Users, data: dict) -> models.Users:
        try:
            for field, value in data.items():
                if value is not None:
                    setattr(user, field, value)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed: Data conflict (email might be in use)."
            )

    @staticmethod
    async def delete_user(db: AsyncSession, user: models.Users) -> None:
        await db.delete(user)
        await db.commit()