from fastapi import Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import Hash
from app.auth import jwt_token
from fastapi.security import  OAuth2PasswordRequestForm
from typing import Annotated
from app.api.v1.user.models import Users
from sqlalchemy.future import select


async def login(request: Annotated[OAuth2PasswordRequestForm, Depends()],db:AsyncSession= Depends(get_db)):

    
    available = await db.execute(select(Users).where(Users.email == request.username))
    user = available.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Incorrect password or username',
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not Hash.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Incorrect password or username',
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User account is inactive. Please contact administrator.'
        )
    
    #  create token
    access_token = jwt_token.create_access_token(data = {
       "sub": str(user.id)
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
