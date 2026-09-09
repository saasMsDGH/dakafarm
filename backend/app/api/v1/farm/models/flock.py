from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from sqlalchemy.sql import func

class Flock(Base):
    __tablename__ = "flocks"

    id = Column(Integer, primary_key=True, index=True)
    flock_code = Column(String, unique=True, index=True, nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id", ondelete="RESTRICT"), nullable=False)
    breed = Column(String, nullable=True)
    initial_quantity = Column(Integer, nullable=False)
    arrival_date = Column(Date, nullable=False)
    status = Column(String, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime (timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),server_default=func.now())

    # Relationships
    house = relationship("House", back_populates="flocks")
    user = relationship("Users")  # Link to creator
    feed_records = relationship("FeedRecord", back_populates="flock", cascade="all, delete-orphan")
    production_records = relationship("ProductionRecord", back_populates="flock", cascade="all, delete-orphan")
