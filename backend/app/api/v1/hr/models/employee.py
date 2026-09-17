from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), index=True, nullable=False)
    last_name = Column(String(100), index=True, nullable=False)
    position = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    employment_date = Column(Date, nullable=True)
    status = Column(Boolean, default=True)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("Users")
    payrolls = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")
