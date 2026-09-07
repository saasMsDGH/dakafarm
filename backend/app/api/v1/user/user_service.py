from app.api.v1.user.repository import UserRepo
from app.api.v1.user import schemas,models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status





class UserService:
    @staticmethod
    async def CreateUser_service(
         request:schemas.User,
         db:Session
    ):
         user = models.Users( 
            first_name = request.first_name,
            last_name = request.last_name,
            email = request.email,
            phone = request.phone,
            password_hash = request.password_hash 
        )

              
         
         

         return await UserRepo.createUser(db,user)

