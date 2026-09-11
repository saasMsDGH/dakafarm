from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.api.v1.inventory.schemas.ProductCategorySchema import ProductCategoryResponse

# ── Request schemas ────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Unique product name")
    category_id: int = Field(..., description="ID of the product category")
    unit_of_measure: str = Field(..., min_length=1, max_length=50, description="e.g., kg, bags, liters")
    unit_price: Optional[Decimal] = Field(Decimal('0.00'), description="Default cost per unit")
    selling_price: Optional[Decimal] = Field(Decimal('0.00'), description="Default selling price")
    reorder_level: Optional[Decimal] = Field(Decimal('0.000'), description="Low stock alert threshold")
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(True, description="Active status")

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = None
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50)
    unit_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

# ── Response schemas ───────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    unit_of_measure: str
    unit_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    current_stock: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    limit: int
    pages: int
