from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    
    movement_type = Column(String(20), nullable=False)  # IN, OUT, ADJUSTMENT
    quantity = Column(Numeric(15, 3), nullable=False)
    
    unit_cost_snapshot = Column(Numeric(20, 6), nullable=True)
    cost_total_fcfa = Column(BigInteger, nullable=True)
    valuation_basis = Column(String(24), nullable=True)

    reference_type = Column(String(100), nullable=True) # e.g., FeedRecord, Purchase
    reference_id = Column(Integer, nullable=True)
    
    movement_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="movements")
    user = relationship("Users")
