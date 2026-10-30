from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

SourceType = Literal['SALE', 'PURCHASE', 'EXPENSE', 'CASH', 'STOCK', 'PRODUCTION', 'FEED', 'VACCINATION', 'MEDICATION', 'MORTALITY', 'PAYROLL_ALLOC']


class ActivityCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    code: str = Field(pattern=r'^[A-Z0-9_-]{2,40}$')
    name: str = Field(min_length=2, max_length=120)
    currency: Literal['XOF'] = 'XOF'


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    activity_id: int = Field(gt=0)
    code: str = Field(pattern=r'^[A-Z0-9_-]{2,40}$')
    name: str = Field(min_length=2, max_length=120)
    start_date: date
    end_date: date | None = None

    @model_validator(mode='after')
    def dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError('La fin doit suivre le début de la campagne.')
        return self


class AssignmentCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    client_operation_id: UUID
    source_type: SourceType
    source_id: int = Field(gt=0)
    source_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    confirm_currency: Literal['XOF']
    reason: str = Field(min_length=3, max_length=1000)


class ReleaseCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    client_operation_id: UUID
    reason: str = Field(min_length=3, max_length=1000)


class OpeningValuation(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    client_operation_id: UUID
    expected_quantity: Decimal = Field(ge=0, max_digits=15, decimal_places=3)
    unit_cost: Decimal = Field(gt=0, max_digits=20, decimal_places=6)
    confirm_currency: Literal['XOF']
    reason: str = Field(min_length=3, max_length=1000)
