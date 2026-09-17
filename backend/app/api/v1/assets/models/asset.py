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
    purchase_date = Column(Date, nullable=True)
    cost_price = Column(Numeric(15, 2), default=0.00)
    quantity = Column(Integer, default=1, nullable=False) # Added quantity for bulk assets
    condition = Column(String(50), default="Good") # e.g. New, Good, Fair, Poor
    depreciation_rate = Column(Numeric(5, 2), default=0.00) # percentage
    status = Column(String(50), default="Active") # e.g. Active, Maintenance, Disposed

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("Users")
    distributions = relationship("AssetDistribution", back_populates="asset", cascade="all, delete-orphan")


class AssetDistribution(Base):
    __tablename__ = "asset_distributions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    location = Column(String(150), nullable=False)
    quantity = Column(Integer, nullable=False)
    assigned_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    asset = relationship("Asset", back_populates="distributions")
    user = relationship("Users")
