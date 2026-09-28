from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MedicationRecord(Base):
    __tablename__ = "medication_records"

    id = Column(Integer, primary_key=True, index=True)
    flock_id = Column(Integer, ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False)
    
    # Strict reference to products
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    
    record_date = Column(Date, nullable=False)
    disease_suspected = Column(String(255), nullable=True)
    
    quantity_used = Column(Numeric(10, 2), nullable=False)
    cost_per_unit = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(12, 2), nullable=True)
    
    withdrawal_period_days = Column(Integer, nullable=False, default=0)
    
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Required timezone syntax
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    flock = relationship("Flock", back_populates="medication_records")
    product = relationship("Product", back_populates="medication")
    user = relationship("Users")  # Recorded by user
