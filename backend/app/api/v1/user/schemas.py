from pydantic import BaseModel,EmailStr
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password_hash: str
    role: Optional[str] = "Farm Worker"  # Default role for new users


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role_name: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    limit: int
    pages: int


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class UserPasswordReset(BaseModel):
    old_password: Optional[str] = None
    new_password: str
