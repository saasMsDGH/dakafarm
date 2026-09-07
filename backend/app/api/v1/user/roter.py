from fastapi import APIRouter,Depends
from app.api.v1.user.user_service import UserService
from app.api.v1.user import schemas
from app.core.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/user",
    tags=["USER"]
)

@router.post("/")
async def post_user(
    request:schemas.User,
    db:Session=Depends(get_db)
):
    return await UserService.CreateUser_service(request,db)
