"""Axes analytiques et preuves de rattachement, sans seconde comptabilité."""
from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Column, Date, DateTime,
                        ForeignKey, Integer, Numeric, String, Text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class DemoDataset(Base):
    __tablename__ = 'demo_datasets'
    id = Column(String(50), primary_key=True)
    as_of = Column(Date, nullable=False)
    manifest = Column(JSONB, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class DemoSource(Base):
    __tablename__ = 'demo_sources'
    source_type = Column(String(30), primary_key=True)
    source_id = Column(Integer, primary_key=True)
    dataset_id = Column(String(50), ForeignKey('demo_datasets.id', ondelete='RESTRICT'), nullable=False)


class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    currency = Column(String(3), nullable=False, default='XOF')
    is_active = Column(Boolean, nullable=False, default=True)
    demo_dataset = Column(String(50), ForeignKey('demo_datasets.id', ondelete='RESTRICT'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (CheckConstraint("currency = 'XOF'", name='ck_activity_currency'),)


class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='RESTRICT'), nullable=False, index=True)
    code = Column(String(40), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(12), nullable=False, default='OPEN')
    created_by = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR end_date >= start_date', name='ck_campaign_dates'),
        CheckConstraint("status IN ('OPEN', 'CLOSED')", name='ck_campaign_status'),
    )


class CampaignEvent(Base):
    __tablename__ = 'campaign_events'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id', ondelete='RESTRICT'), nullable=False, index=True)
    source_type = Column(String(30), nullable=False)
    source_id = Column(Integer, nullable=False)
    action = Column(String(10), nullable=False)
    previous_event_id = Column(BigInteger, ForeignKey('campaign_events.id', ondelete='RESTRICT'), unique=True)
    client_operation_id = Column(String(36), unique=True, nullable=False)
    payload_hash = Column(String(64), nullable=False)
    source_hash = Column(String(64), nullable=False)
    snapshot = Column(JSONB, nullable=False)
    reason = Column(Text, nullable=False)
    actor_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("action IN ('ASSIGN', 'RELEASE')", name='ck_campaign_event_action'),
        CheckConstraint('source_id > 0', name='ck_campaign_event_source_id'),
    )


class ProductValuation(Base):
    __tablename__ = 'product_valuations'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = Column(Numeric(20, 6), nullable=False)
    unit_cost = Column(Numeric(20, 6), nullable=False)
    basis = Column(String(24), nullable=False)
    origin = Column(String(20), nullable=False)
    purchase_id = Column(Integer, ForeignKey('purchases.id', ondelete='RESTRICT'), nullable=True)
    client_operation_id = Column(String(36), unique=True, nullable=True)
    payload_hash = Column(String(64), nullable=True)
    reason = Column(Text, nullable=False)
    actor_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (CheckConstraint('quantity >= 0 AND unit_cost >= 0', name='ck_product_valuation_positive'),)
