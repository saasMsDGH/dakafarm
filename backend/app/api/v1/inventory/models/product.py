from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(100), index=True, nullable=False)
    unit_of_measure = Column(String(50), nullable=False) # e.g., kg, liters, bags
    unit_price = Column(Numeric(20, 6), default=0.00)
    cost_basis = Column(String(24), nullable=False, default="UNVERIFIED", server_default="UNVERIFIED")
    selling_price = Column (Numeric(15,2) , default =0.00)
    current_stock = Column(Numeric(15, 3), default=0.000)
    reorder_level = Column(Numeric(15, 3), default=0.000)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Required timezone syntax
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    category = relationship("ProductCategory")
    user = relationship("Users")
    movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    feed_record = relationship("FeedRecord",back_populates="product")
    medication = relationship("MedicationRecord", back_populates="product")
    vaccination = relationship("VaccinationRecord", back_populates="product")

