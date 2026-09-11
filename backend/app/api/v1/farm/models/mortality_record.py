from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MortalityRecord(Base):
    __tablename__ = "mortality_records"

    id = Column(Integer, primary_key=True, index=True)
    flock_id = Column(Integer, ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False)
    
    record_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    cause = Column(String(255), nullable=True)
    
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Required timezone syntax
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    flock = relationship("Flock", back_populates="mortality_records")
    user = relationship("Users")  # Recorded by user
