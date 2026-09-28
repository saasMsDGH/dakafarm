from fastapi import Depends,HTTPException,status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from app.auth import jwt_token
from sqlalchemy.ext.asyncio import AsyncSession 
from app.core.database import get_db



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return await jwt_token.verify_token(token, credentials_exception, db)

async def get_optional_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)] = None,
    db: AsyncSession = Depends(get_db)
):
    if not token:
        return None
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return await jwt_token.verify_token(token, credentials_exception, db)
    except Exception:
        return None