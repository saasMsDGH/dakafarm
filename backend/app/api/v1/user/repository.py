
from app.api.v1.user import models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,status






class UserRepo:
    @staticmethod
    async def createUser(db:Session,user:models.Users):

        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                               status_code=400,detail="conflicts: data already exesist"
                          )

        return user
