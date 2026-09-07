from pydantic import BaseModel
from datetime import date


class User(BaseModel):
    first_name : str
    last_name : str
    email :str
    phone : str 
    password_hash : str


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









