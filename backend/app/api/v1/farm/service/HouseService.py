from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.farm.repository.HouseRepo import HouseRepo
from app.api.v1.farm.models import house as house_model
from app.api.v1.farm.schemas import HouseSchema



class House_service:
    @staticmethod
    async def createHouse(db:AsyncSession,request:HouseSchema.CreateHouse,current_user:int):
        new_house = house_model.House(
            name = request.name,
            location = request.location,
            capacity = request.capacity,
            description = request.description,
            created_by = current_user

        )

        new_house = await HouseRepo.create_house(db,house=new_house)

        return new_house


