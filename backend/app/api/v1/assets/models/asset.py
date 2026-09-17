from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), index=True, nullable=False)
    description = Column(Text, nullable=True)
    serial_number = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    cost_price = Column(Numeric(15, 2), default=0.00)
    location = Column(String(150), nullable=True)
    condition = Column(String(50), default="Good") # e.g. New, Good, Fair, Poor
    depreciation_rate = Column(Numeric(5, 2), default=0.00) # percentage
    status = Column(String(50), default="Active") # e.g. Active, Maintenance, Disposed

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("Users")
