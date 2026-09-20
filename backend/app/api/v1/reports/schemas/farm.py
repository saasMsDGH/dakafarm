from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class ProductionRecordItem(BaseModel):
    id: int
    record_date: date
    flock_code: Optional[str] = None
    house_name: Optional[str] = None
    total_birds: Optional[int] = None
    total_eggs: Optional[int] = None
    damaged_eggs: Optional[int] = None
    good_eggs: Optional[int] = None
    laying_percentage: Optional[Decimal] = None
    recorded_by: Optional[int] = None

    model_config = {"from_attributes": True}


class ProductionSummaryReport(BaseModel):
    items: List[ProductionRecordItem]
    total: int
    page: int
    limit: int
    pages: int
    total_eggs: int
    total_good_eggs: int
    total_damaged_eggs: int
    avg_laying_pct: Optional[Decimal] = None


class ProductionByFlockItem(BaseModel):
    flock_id: int
    flock_code: str
    house_name: Optional[str] = None
    bird_population: Optional[int] = None
    total_eggs: int
    damaged_eggs: int
    good_eggs: int
    avg_laying_pct: Optional[Decimal] = None


class ProductionByHouseItem(BaseModel):
    house_id: int
    house_name: str
    total_eggs: int
    good_eggs: int
    damaged_eggs: int
    avg_laying_pct: Optional[Decimal] = None


class FeedUsageItem(BaseModel):
    id: int
    record_date: date
    flock_code: Optional[str] = None
    house_name: Optional[str] = None
    product_name: Optional[str] = None
    opening_quantity: Optional[Decimal] = None
    quantity_used: Decimal
    closing_quantity: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class FeedUsageReport(BaseModel):
    items: List[FeedUsageItem]
    total: int
    page: int
    limit: int
    pages: int
    total_cost: Decimal
    total_quantity_used: Decimal


class FeedByFlockItem(BaseModel):
    flock_id: int
    flock_code: str
    product_name: Optional[str] = None
    quantity_used: Decimal
    total_cost: Decimal


class MedicationItem(BaseModel):
    id: int
    record_date: date
    flock_code: Optional[str] = None
    product_name: Optional[str] = None
    disease_suspected: Optional[str] = None
    quantity_used: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    withdrawal_period_days: Optional[int] = None
    recorded_by: Optional[int] = None

    model_config = {"from_attributes": True}


class MedicationReport(BaseModel):
    items: List[MedicationItem]
    total: int
    page: int
    limit: int
    pages: int
    total_cost: Decimal


class VaccinationItem(BaseModel):
    id: int
    record_date: date
    flock_code: Optional[str] = None
    product_name: Optional[str] = None
    disease_targeted: Optional[str] = None
    administration_method: Optional[str] = None
    quantity_used: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    next_due_date: Optional[date] = None
    recorded_by: Optional[int] = None

    model_config = {"from_attributes": True}


class VaccinationReport(BaseModel):
    items: List[VaccinationItem]
    total: int
    page: int
    limit: int
    pages: int


class MortalitySummaryReport(BaseModel):
    total_deaths: int
    num_flocks_affected: int
    period_from: Optional[str] = None
    period_to: Optional[str] = None


class MortalityByFlockItem(BaseModel):
    flock_id: int
    flock_code: str
    initial_population: int
    total_deaths: int
    remaining_birds: int
    mortality_rate: Decimal


class MortalityByCauseItem(BaseModel):
    cause: str
    num_records: int
    total_deaths: int
    percentage: Decimal
