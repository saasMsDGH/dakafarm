from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.api.v1.user.repository import UserRepo
from app.api.v1.user import schemas, models
from app.core.security import Hash
from app.shared.pagination import PaginationParams, compute_pages


class UserService:
    
    @staticmethod
    def _extract_primary_role(user: models.Users) -> str:
        """Helper to extract the string name of the user's role."""
        if user.role and len(user.role) > 0 and user.role[0].roleid:
            return user.role[0].roleid.name
        return "Unknown"

    @staticmethod
    def _to_response(user: models.Users) -> schemas.UserResponse:
        """Helper to map model to UserResponse."""
        resp = schemas.UserResponse.model_validate(user)
        resp.role_name = UserService._extract_primary_role(user)
        return resp

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
        
        # Load relationships for proper response
        full_user = await UserRepo.get_user_by_id(db, user.id)
        return UserService._to_response(full_user)

    @staticmethod
    async def get_me(db: AsyncSession, current_user_id: int) -> schemas.UserResponse:
        user = await UserRepo.get_user_by_id(db, current_user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserService._to_response(user)

    @staticmethod
    async def get_all_roles(db: AsyncSession):
        roles = await UserRepo.get_all_roles(db)
        return [{"id": r.id, "name": r.name} for r in roles]

    @staticmethod
    async def get_all_users(db: AsyncSession, params: PaginationParams) -> schemas.UserListResponse:
        users, total = await UserRepo.list_users(db, params)
        items = [UserService._to_response(u) for u in users]
        return schemas.UserListResponse(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )

    @staticmethod
    async def update_user(
        db: AsyncSession, 
        target_user_id: int, 
        request: schemas.UserUpdate, 
        current_user: models.Users
    ) -> schemas.UserResponse:
        
        # 1. Fetch current user role info to verify permissions
        full_current_user = await UserRepo.get_user_by_id(db, current_user.id)
        is_admin = UserService._extract_primary_role(full_current_user) == "admin"
        
        # Permission check
        if current_user.id != target_user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this user."
            )

        # 2. Fetch target user
        target_user = await UserRepo.get_user_by_id(db, target_user_id)
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # 3. Prevent non-admins from updating roles
        update_data = request.model_dump(exclude_unset=True)
        new_role_name = update_data.pop("role", None)
        new_is_active = update_data.pop("is_active", None)
        
        if new_is_active is not None:
            if not is_admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can change active status.")
            update_data["is_active"] = new_is_active

        if new_role_name:
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can change roles."
                )
            
            # Find new role
            role_record = await UserRepo.get_role(db, new_role_name)
            if not role_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role '{new_role_name}' does not exist."
                )
                
            # Update user's role mapping
            if target_user.role:
                target_user.role[0].role_id = role_record.id
            else:
                user_role = models.UserRole(user_id=target_user.id, role_id=role_record.id)
                db.add(user_role)

        # 4. Apply standard updates
        updated_user = await UserRepo.update_user(db, target_user, update_data)
        
        # Ensure relationships are loaded fully
        final_user = await UserRepo.get_user_by_id(db, updated_user.id, force_refresh=True)
        return UserService._to_response(final_user)

    @staticmethod
    async def delete_user(
        db: AsyncSession, 
        target_user_id: int, 
        current_user: models.Users
    ) -> None:
        
        # Permission check
        full_current_user = await UserRepo.get_user_by_id(db, current_user.id)
        is_admin = UserService._extract_primary_role(full_current_user) == "admin"
        
        if current_user.id != target_user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this user."
            )

        target_user = await UserRepo.get_user_by_id(db, target_user_id)
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        await UserRepo.delete_user(db, target_user)

    @staticmethod
    async def reset_password(
        db: AsyncSession, 
        target_user_id: int, 
        request: schemas.UserPasswordReset, 
        current_user: models.Users
    ) -> schemas.UserResponse:
        # Permission check
        full_current_user = await UserRepo.get_user_by_id(db, current_user.id)
        is_admin = UserService._extract_primary_role(full_current_user) == "admin"
        
        if current_user.id != target_user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to reset this user's password."
            )

        target_user = await UserRepo.get_user_by_id(db, target_user_id)
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # Logic for Normal User
        if not is_admin:
            if not request.old_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="old_password is required to change your password."
                )
            # Verify old password
            if not Hash.verify_password(request.old_password, target_user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Invalid old password."
                )

        if request.new_password == request.old_password:
            raise HTTPException(status_code=400,detail="password mpya imefanana na yazamani")

        # Hash new password and save
        hashed_new_password = Hash.hash(request.new_password)


        await UserRepo.update_user(db, target_user, {"password_hash": hashed_new_password})
        
        # Reload to eagerly load relationships for response
        final_user = await UserRepo.get_user_by_id(db, target_user_id, force_refresh=True)
        return UserService._to_response(final_user)