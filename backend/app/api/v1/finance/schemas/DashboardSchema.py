from pydantic import BaseModel
from decimal import Decimal

class FinanceDashboardResponse(BaseModel):
    # Lifetime / Current Balances
    cash_on_hand: Decimal
    accounts_receivable: Decimal
    accounts_payable: Decimal
    
    # Current Month Performance
    monthly_revenue: Decimal
    monthly_expenses: Decimal
    monthly_net_profit: Decimal
