from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateHouse(BaseModel):
    name : str
    location : Optional[str] = None
    capacity : Optional[int] = None
    description : Optional[str] = None

class ResponceHouse(BaseModel):
    id : int
    loaction : Optional[str]=None
    capacity : Optional[int] = None
    description : Optional[str] = None
    created_at : Optional[datetime] = None

    class Config:
     from_attributes = True




