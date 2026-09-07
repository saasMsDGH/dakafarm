from fastapi import APIRouter
from app.api.v1.user import roter as user_router

router = APIRouter(
    prefix="/v1"
   
)

router.include_router(user_router.router)