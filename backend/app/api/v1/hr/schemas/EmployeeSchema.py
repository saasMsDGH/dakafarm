from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# --- Request Schemas ---

class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100, description="Employee first name")
    last_name: str = Field(..., min_length=2, max_length=100, description="Employee last name")
    position: str = Field(..., min_length=2, max_length=100, description="Job position/title")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    employment_date: Optional[date] = Field(None, description="Date of employment")
    status: Optional[bool] = Field(True, description="Active status")

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    position: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    employment_date: Optional[date] = Field(None)
    status: Optional[bool] = Field(None)

# --- Response Schemas ---

class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    position: str
    phone: Optional[str]
    employment_date: Optional[date]
    status: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class EmployeeListResponse(BaseModel):
    items: List[EmployeeResponse]
    total: int
    page: int
    limit: int
    pages: int
