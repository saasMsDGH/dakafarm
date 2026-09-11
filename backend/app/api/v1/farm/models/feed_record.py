from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FeedRecord(Base):
    __tablename__ = "feed_records"

    id = Column(Integer, primary_key=True, index=True)
    flock_id = Column(Integer, ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False)
    
    # Strict reference to products
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True) 

    record_date = Column(Date, nullable=False)
    
    # Numeric types matching standard DB specification
    opening_quantity = Column(Numeric(15, 3), nullable=True)
    quantity_used = Column(Numeric(15, 3), nullable=False)
    closing_quantity = Column(Numeric(15, 3), nullable=True)
    
    cost_per_unit = Column(Numeric(15, 2), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Required timezone syntax
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    flock = relationship("Flock", back_populates="feed_records")
    product = relationship("Prosuct",back_populates="feed_record")
    user = relationship("Users")  # Recorded by user
