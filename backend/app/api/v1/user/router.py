from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.user.user_service import UserService
from app.api.v1.user import schemas
from app.api.v1.user.models import Users
from app.core.database import get_db
from app.auth.auth import get_current_user
from app.auth.RoleAuth import RoleChecker
from app.shared.pagination import PaginationParams

admin_only = RoleChecker(["admin"])

router = APIRouter(
    prefix="/user",
    tags=["USER"]
)

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def post_user(
    request: schemas.User,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    return await UserService.CreateUser_service(request, db)


@router.get("/me", response_model=schemas.UserResponse)
async def get_me_endpoint(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current authenticated user's profile."""
    return await UserService.get_me(db, current_user.id)


@router.get("/roles")
async def get_roles_endpoint(
    db: AsyncSession = Depends(get_db)
):
    """Get all available roles."""
    return await UserService.get_all_roles(db)


@router.get("/", response_model=schemas.UserListResponse)
async def list_users_endpoint(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    current_user: Users = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """List all users (Admin only)."""
    params = PaginationParams(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order
    )
    return await UserService.get_all_users(db, params)


@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user_endpoint(
    user_id: int,
    request: schemas.UserUpdate,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user.
    - Users can update their own profile.
    - Admins can update any user's profile.
    - Only Admins can change roles.
    """
    return await UserService.update_user(db, user_id, request, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user.
    - Users can delete their own account.
    - Admins can delete any user.
    """
    return await UserService.delete_user(db, user_id, current_user)


@router.put("/{user_id}/password", response_model=schemas.UserResponse)
async def reset_password_endpoint(
    user_id: int,
    request: schemas.UserPasswordReset,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a user's password.
    - Users must provide 'old_password' to change their own password.
    - Admins can bypass 'old_password' to reset anyone's password directly.
    """
    return await UserService.reset_password(db, user_id, request, current_user)
