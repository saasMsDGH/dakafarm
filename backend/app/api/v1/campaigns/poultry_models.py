"""Liens de campagne avicole et ventilation salariale sans seconde paie."""
from sqlalchemy import BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class PoultryCampaign(Base):
    __tablename__ = 'poultry_campaigns'
    campaign_id = Column(Integer, ForeignKey('campaigns.id', ondelete='RESTRICT'), primary_key=True)
    flock_id = Column(Integer, ForeignKey('flocks.id', ondelete='RESTRICT'), nullable=False, unique=True)
    bird_product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    egg_product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    feed_product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    vaccine_product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    assumptions = Column(JSONB, nullable=False)


class PayrollAllocation(Base):
    __tablename__ = 'payroll_allocations'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    payroll_id = Column(Integer, ForeignKey('payrolls.id', ondelete='RESTRICT'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id', ondelete='RESTRICT'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False)
    allocation_date = Column(Date, nullable=False)
    amount_fcfa = Column(BigInteger, nullable=False)
    payroll_net_fcfa = Column(BigInteger, nullable=False)
    pay_period = Column(String(50), nullable=False)
    method = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (UniqueConstraint('payroll_id','campaign_id',name='uq_payroll_campaign'),
        CheckConstraint('amount_fcfa >= 0 AND payroll_net_fcfa >= amount_fcfa',name='ck_payroll_allocation_amount'))


class RetiredDemoSource(Base):
    __tablename__ = 'retired_demo_sources'
    source_type = Column(String(30), primary_key=True)
    source_id = Column(Integer, primary_key=True)
    extension_id = Column(String(50), ForeignKey('demo_datasets.id', ondelete='RESTRICT'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
