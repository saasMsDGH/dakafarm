import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import jwt
from app.auth import jwtToken
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.user.models import Users
from app.core.config import settings
from sqlalchemy.future import select

load_dotenv()

SECRET_KEY = (settings.SECRET_KEY)
ALGORITHM = (settings.ALGORITHM)


ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str,credentials_exception,db:AsyncSession):
   try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = jwtToken.TokenData(email=user_id)
   except InvalidTokenError:
        raise credentials_exception

   available =await db.execute(select(Users).where(Users.id == int(user_id)))
   user = available.scalar_one_or_none()

   if user is None:
        raise credentials_exception

   if not user.is_active:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

   return user