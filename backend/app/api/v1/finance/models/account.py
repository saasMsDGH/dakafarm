from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class FinancialAccount(Base):
    __tablename__ = "financial_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    account_type = Column(String(50), nullable=False, index=True) # CASH, BANK, MOBILE_MONEY
    bank_name = Column(String(150), nullable=True)
    account_number = Column(String(100), nullable=True)
    opening_balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("Users")
