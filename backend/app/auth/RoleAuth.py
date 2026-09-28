from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import get_current_user
from app.api.v1.user.models import Users, UserRole
from app.core.database import get_db


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = set(allowed_roles)

    async def __call__(
        self,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Users:

        result = await db.execute(
            select(Users)
            .options(
                selectinload(Users.role)
                .selectinload(UserRole.roleid)
            )
            .where(Users.id == current_user.id)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        user_roles = {
            user_role.roleid.name
            for user_role in user.role
            if user_role.roleid is not None
        }

        # Admin bypass
        if "admin" in user_roles:
            return user

        # Check allowed roles
        if not user_roles.intersection(self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return user