from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.BalanceSheetRepo import BalanceSheetRepo
from app.api.v1.finance.repository.PnLRepo import PnLRepo
from app.api.v1.finance.schemas.DashboardSchema import FinanceDashboardResponse

class DashboardService:
    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> FinanceDashboardResponse:
        
        # 1. Get Lifetime Balances (No date filter)
        bs_data = await BalanceSheetRepo.generate_balance_sheet(db, as_of_date=None)
        
        cash_on_hand = bs_data["cash_and_bank"]
        from sqlalchemy import select, func
        from app.api.v1.pos.models.sale import Sale
        from app.api.v1.pos.models.purchase import Purchase
        from decimal import Decimal

        ar_q = await db.execute(select(func.sum(Sale.total_amount - Sale.amount_paid)).where(Sale.payment_status.in_(['UNPAID', 'PARTIAL'])))
        accounts_receivable = ar_q.scalar() or Decimal('0.00')
        
        ap_q = await db.execute(select(func.sum(Purchase.total_amount - Purchase.amount_paid)).where(Purchase.payment_status.in_(['UNPAID', 'PARTIAL'])))
        accounts_payable = ap_q.scalar() or Decimal('0.00')
        
        # 2. Get Period Performance
        if not start_date and not end_date:
            now = datetime.now(timezone.utc)
            start_date = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        pnl_data = await PnLRepo.generate_pnl(db, start_date=start_date, end_date=end_date)
        
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
