from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    pay_period = Column(String(50), nullable=False) # e.g. "September 2026" or "2026-09"
    basic_salary = Column(Numeric(15, 2), nullable=False)
    allowances = Column(Numeric(15, 2), default=0.00)
    deductions = Column(Numeric(15, 2), default=0.00)
    net_salary = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), nullable=False, default=0.00)
    payment_date = Column(Date, nullable=True)
    payment_status = Column(String(50), default="UNPAID") # UNPAID, PARTIAL, PAID

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    employee = relationship("Employee", back_populates="payrolls")
    user = relationship("Users")
    payments = relationship("PayrollPayment", back_populates="payroll", cascade="all, delete-orphan")
