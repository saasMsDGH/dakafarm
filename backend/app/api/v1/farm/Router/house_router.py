from fastapi import APIRouter,Depends
from app.api.v1.farm.models import house
from app.api.v1.user.models import Users
from app.api.v1.farm.schemas import HouseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.farm.service.HouseService import House_service 
from app.auth .RoleAuth import RoleChecker

farm_worker = RoleChecker(["admin"])




router = APIRouter(
    tags=["House"],
    prefix="/house"
)

@router.post("/",response_model=HouseSchema.ResponceHouse)
async def Post_house(request:HouseSchema.CreateHouse,current_user:Users=Depends(farm_worker),db:AsyncSession=Depends(get_db)):
    return await House_service.createHouse(db,request,current_user.id)

