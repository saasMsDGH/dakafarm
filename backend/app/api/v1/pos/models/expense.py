from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_number = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # Free text: Transport, Electricity, Salary, etc.
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), nullable=False, default=0.00)
    payment_status = Column(String(20), nullable=False, default="UNPAID") # PAID, PARTIAL, UNPAID
    expense_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String(50), nullable=True)  # Deprecated, moved to expense_payments

    paid_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("Users")
    payments = relationship("ExpensePayment", back_populates="expense", cascade="all, delete-orphan")

