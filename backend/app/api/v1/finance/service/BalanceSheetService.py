from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.BalanceSheetRepo import BalanceSheetRepo
from app.api.v1.finance.schemas.BalanceSheetSchema import (
    BalanceSheetResponse, AssetsSection, LiabilitiesSection, EquitySection
)

class BalanceSheetService:
    @staticmethod
    async def get_balance_sheet(db: AsyncSession, as_of_date: Optional[datetime] = None) -> BalanceSheetResponse:
        
        data = await BalanceSheetRepo.generate_balance_sheet(db, as_of_date)
        
        # 1. Assets
        total_assets = (
            data["cash_and_bank"] + 
            data["accounts_receivable"] + 
            data["prepaid_purchases"] + 
            data["fixed_assets"]
        )
        assets = AssetsSection(
            cash_and_bank=data["cash_and_bank"],
            accounts_receivable=data["accounts_receivable"],
            prepaid_purchases=data["prepaid_purchases"],
            fixed_assets=data["fixed_assets"],
            total_assets=total_assets
        )
        
        # 2. Liabilities
        total_liabilities = data["accounts_payable"] + data["unearned_revenue"]
        liabilities = LiabilitiesSection(
            accounts_payable=data["accounts_payable"],
            unearned_revenue=data["unearned_revenue"],
            total_liabilities=total_liabilities
        )
        
        # 3. Equity
        total_equity = data["owner_capital"] + data["retained_earnings"]
        equity = EquitySection(
            owner_capital=data["owner_capital"],
            retained_earnings=data["retained_earnings"],
            total_equity=total_equity
        )
        
        # Verification
        is_balanced = total_assets == (total_liabilities + total_equity)
        
        return BalanceSheetResponse(
            as_of_date=as_of_date,
            assets=assets,
            liabilities=liabilities,
            equity=equity,
            is_balanced=is_balanced
        )
