from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.finance.repository.PnLRepo import PnLRepo
from app.api.v1.finance.schemas.PnLSchema import (
    PnLResponse, RevenueSection, COGSSection, OPEXSection, NonOperatingSection
)

class PnLService:
    @staticmethod
    async def get_pnl(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> PnLResponse:
        
        data = await PnLRepo.generate_pnl(db, start_date, end_date)
        
        # 1. Revenue
        sales = data["sales"]
        total_revenue = sales
        revenue_section = RevenueSection(sales=sales, total_revenue=total_revenue)
        
        # 2. COGS
        purchases = data["purchases"]
        total_cogs = purchases
        cogs_section = COGSSection(purchases=purchases, total_cogs=total_cogs)
        
        # Gross Profit
        gross_profit = total_revenue - total_cogs
        
        # 3. OPEX
        direct_expenses = data["direct_expenses"]
        payroll = data["payroll"]
        neg_adj = data["negative_adjustments"]
        total_opex = direct_expenses + payroll + neg_adj
        
        opex_section = OPEXSection(
            direct_expenses=direct_expenses,
            payroll=payroll,
            negative_adjustments=neg_adj,
            total_opex=total_opex
        )
        
        # Operating Profit
        operating_profit = gross_profit - total_opex
        
        # 4. Non-Operating
        other_income = data["other_income"]
        pos_adj = data["positive_adjustments"]
        uncat_in = data["uncategorized_income"]
        uncat_out = data["uncategorized_expense"]
        
        total_non_operating = (other_income + pos_adj + uncat_in) - uncat_out
        
        non_op_section = NonOperatingSection(
            other_income=other_income,
            positive_adjustments=pos_adj,
            uncategorized_income=uncat_in,
            uncategorized_expense=uncat_out,
            total_non_operating=total_non_operating
        )
        
        # Net Profit
        net_profit = operating_profit + total_non_operating
        
        return PnLResponse(
            start_date=start_date,
            end_date=end_date,
            revenue=revenue_section,
            cogs=cogs_section,
            gross_profit=gross_profit,
            opex=opex_section,
            operating_profit=operating_profit,
            non_operating=non_op_section,
            net_profit=net_profit
        )
