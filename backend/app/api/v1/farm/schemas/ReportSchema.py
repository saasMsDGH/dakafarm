from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional

class FarmReportResponse(BaseModel):
    start_date: date
    end_date: date
    
    total_eggs: int = 0
    good_eggs: int = 0
    damaged_eggs: int = 0
    
    total_mortality: int = 0
    
    total_feed_used: Decimal = Decimal('0.0')
    total_feed_cost: Decimal = Decimal('0.0')
    
    total_medication_cost: Decimal = Decimal('0.0')
    total_vaccination_cost: Decimal = Decimal('0.0')
    
    total_expenses: Decimal = Decimal('0.0')

    model_config = {"from_attributes": True}
