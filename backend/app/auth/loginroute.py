from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession  
from app.core.database import get_db
from typing import Annotated
from app.auth import authentication
from fastapi.security import OAuth2PasswordRequestForm



router = APIRouter(tags=["authentication"])

@router.post("/login")
async def login(request: Annotated[OAuth2PasswordRequestForm, Depends()], database: AsyncSession = Depends(get_db)):
    return await authentication.login(request, database)

