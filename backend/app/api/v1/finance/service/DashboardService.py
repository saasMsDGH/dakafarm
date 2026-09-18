from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.BalanceSheetRepo import BalanceSheetRepo
from app.api.v1.finance.repository.PnLRepo import PnLRepo
from app.api.v1.finance.schemas.DashboardSchema import FinanceDashboardResponse

class DashboardService:
    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> FinanceDashboardResponse:
        
        # 1. Get Lifetime Balances (No date filter)
        bs_data = await BalanceSheetRepo.generate_balance_sheet(db, as_of_date=None)
        
        cash_on_hand = bs_data["cash_and_bank"]
        accounts_receivable = bs_data["accounts_receivable"]
        accounts_payable = bs_data["accounts_payable"]
        
        # 2. Get Current Month Performance
        now = datetime.now(timezone.utc)
        first_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        pnl_data = await PnLRepo.generate_pnl(db, start_date=first_of_month, end_date=None)
        
        monthly_revenue = (
            pnl_data["sales"] + 
            pnl_data["other_income"] + 
            pnl_data["positive_adjustments"] + 
            pnl_data["uncategorized_income"]
        )
        
        monthly_expenses = (
            pnl_data["purchases"] + 
            pnl_data["direct_expenses"] + 
            pnl_data["payroll"] + 
            pnl_data["negative_adjustments"] + 
            pnl_data["uncategorized_expense"]
        )
        
        monthly_net_profit = monthly_revenue - monthly_expenses
        
        return FinanceDashboardResponse(
            cash_on_hand=cash_on_hand,
            accounts_receivable=accounts_receivable,
            accounts_payable=accounts_payable,
            monthly_revenue=monthly_revenue,
            monthly_expenses=monthly_expenses,
            monthly_net_profit=monthly_net_profit
        )
