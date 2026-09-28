from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.repository.CashFlowRepo import CashFlowRepo
from app.api.v1.finance.schemas.CashFlowSchema import (
    CashFlowResponse, OperatingFlows, InvestingFlows, FinancingFlows
)

class CashFlowService:
    @staticmethod
    async def get_cash_flow(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> CashFlowResponse:
        
        data = await CashFlowRepo.generate_cash_flow(db, start_date, end_date)
        
        # Operating Flows
        net_operating_cash_flow = (
            data["cash_from_sales"] +
            data["cash_to_suppliers"] +
            data["cash_for_expenses"] +
            data["cash_for_payroll"] +
            data["other_operating_cash"] +
            data["uncategorized_operating_cash"]
        )
        
        operating = OperatingFlows(
            cash_from_sales=data["cash_from_sales"],
            cash_to_suppliers=data["cash_to_suppliers"],
            cash_for_expenses=data["cash_for_expenses"],
            cash_for_payroll=data["cash_for_payroll"],
            other_operating_cash=data["other_operating_cash"],
            uncategorized_operating_cash=data["uncategorized_operating_cash"],
            net_operating_cash_flow=net_operating_cash_flow
        )
        
        # Investing Flows
        net_investing_cash_flow = data["cash_for_assets"]
        
        investing = InvestingFlows(
            cash_for_assets=data["cash_for_assets"],
            net_investing_cash_flow=net_investing_cash_flow
        )
        
        # Financing Flows
        net_financing_cash_flow = data["owner_investments"]
        
        financing = FinancingFlows(
            owner_investments=data["owner_investments"],
            net_financing_cash_flow=net_financing_cash_flow
        )
        
        # Totals
        net_change_in_cash = net_operating_cash_flow + net_investing_cash_flow + net_financing_cash_flow
        opening_balance = data["opening_balance"]
        ending_balance = opening_balance + net_change_in_cash
        
        return CashFlowResponse(
            start_date=start_date,
            end_date=end_date,
            operating=operating,
            investing=investing,
            financing=financing,
            net_change_in_cash=net_change_in_cash,
            opening_balance=opening_balance,
            ending_balance=ending_balance
        )
