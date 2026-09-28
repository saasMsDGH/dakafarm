from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, APIRouter, HTTPException, status,dependencies
from .database import get_db
from app.api.v1.user.models import Roles,Users
from app.auth.auth import get_current_user


router = APIRouter(tags=["Seed"])


DEFAULT_ROLES = [
    {
        "name": "admin",
   
    },
    {
        "name": "finance_manager",
       
    },
    {
        "name": "Farm Manager",
       
    },{
        "name":"hr_officer",
    },{
        "name": "Farm Worker",
    },{
        "name": "inventory_admin",
    },{
        "name":"sell_manager",
    },{
        "name":"sell_officer",
    },{
        "name":"hr_manager",
    },{
        "name":"asset_manager"
    }
] 


@router.post("/db")
async def seed_roles(
    db: AsyncSession = Depends(get_db),
    current_user : Users=Depends(get_current_user)
    
):
    added_any = False

    for role_data in DEFAULT_ROLES:
        exists = (
            await db.execute(select(Roles).where(Roles.name == role_data["name"]))
        )
        roles = exists.scalar_one_or_none()

        if not roles:
            db.add(Roles(**role_data))
            added_any = True

    await db.commit()

    if added_any:
        return {"message": "Roles seeded successfully"}

    return {"message": "seed already planted"}
