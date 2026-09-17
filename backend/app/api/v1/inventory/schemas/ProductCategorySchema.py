from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ── Request schemas ────────────────────────────────────────────────────────────

class ProductCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Unique category name")
    description: Optional[str] = Field(None, max_length=255, description="Category description")
    is_active: Optional[bool] = Field(True, description="Active status")

class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

# ── Response schemas ───────────────────────────────────────────────────────────

class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ProductCategoryListResponse(BaseModel):
    items: List[ProductCategoryResponse]
    total: int
    page: int
    limit: int
    pages: int
