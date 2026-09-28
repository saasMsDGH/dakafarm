from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    flock_id = Column(Integer, ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False)
    
    record_date = Column(Date, nullable=False)
    
    total_birds = Column(Integer, nullable=False)
    total_eggs = Column(Integer, nullable=False)
    damaged_eggs = Column(Integer, nullable=False, default=0)
    
    # Auto-calculated fields
    good_eggs = Column(Integer, nullable=False)
    laying_percentage = Column(Numeric(5, 2), nullable=False)
    
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Required timezone syntax
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    flock = relationship("Flock", back_populates="production_records")
    user = relationship("Users")  # Recorded by user
