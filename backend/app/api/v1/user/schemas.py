from pydantic import BaseModel
from typing import Optional
from datetime import date


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password_hash: str
    role: Optional[str] = "Farm Worker"  # Default role for new users



class UserReseponse(BaseModel):
    id:int
    first_name : str
    last_name : str
    email :str
    phone : str
    password_hash : str
    created_at : date

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    first_name : str
    last_name : str
    email :str
    phone : str 

class UserChangePassword(BaseModel):
    password_hash : str









