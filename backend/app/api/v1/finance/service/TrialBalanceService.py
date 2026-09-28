from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.TrialBalanceRepo import TrialBalanceRepo
from app.api.v1.finance.schemas.TrialBalanceSchema import TrialBalanceResponse

class TrialBalanceService:
    @staticmethod
    async def get_trial_balance(db: AsyncSession, as_of_date: Optional[datetime] = None) -> TrialBalanceResponse:
        # Resolve effective date for the response (if None, use current time)
        effective_date = as_of_date or datetime.utcnow()
        
        entries, total_debits, total_credits = await TrialBalanceRepo.generate_trial_balance(db, as_of_date)
        
        # A mathematical truth of double entry/accounting equations is that DR == CR.
        # We allow a small fractional difference (e.g. 0.01) if floating point rounding ever occurred, 
        # but with Decimal it should be exactly equal.
        is_balanced = (total_debits == total_credits)
        
        return TrialBalanceResponse(
            entries=entries,
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced,
            as_of_date=effective_date
        )
