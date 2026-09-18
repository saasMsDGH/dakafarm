from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount

class CashFlowRepo:
    @staticmethod
    async def generate_cash_flow(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        
        # -------------------------------------------------------------
        # 1. Calculate Opening Balance (Prior to start_date)
        # -------------------------------------------------------------
        total_opening_balance = Decimal('0.00')
        prior_transactions_net = Decimal('0.00')

        # Base accounts opening balance (created before start_date, or all if no start_date)
        acct_q = select(func.sum(FinancialAccount.opening_balance))
        if start_date:
            acct_q = acct_q.where(FinancialAccount.created_at < start_date)
        
        acct_res = await db.execute(acct_q)
        total_opening_balance = Decimal(acct_res.scalar() or '0.00')

        # Prior transactions net (IN - OUT)
        if start_date:
            prior_tx_q = select(
                func.sum(case((FinancialTransaction.direction == 'IN', FinancialTransaction.amount), else_=0)) - 
                func.sum(case((FinancialTransaction.direction == 'OUT', FinancialTransaction.amount), else_=0))
            ).where(FinancialTransaction.transaction_date < start_date)
            
            prior_res = await db.execute(prior_tx_q)
            prior_transactions_net = Decimal(prior_res.scalar() or '0.00')
            
        opening_balance = total_opening_balance + prior_transactions_net

        # -------------------------------------------------------------
        # 2. Calculate Period Flows (start_date <= date <= end_date)
        # -------------------------------------------------------------
        tx_agg_q = select(
            FinancialTransaction.transaction_type,
            func.sum(case((FinancialTransaction.direction == 'IN', FinancialTransaction.amount), else_=0)).label('total_in'),
            func.sum(case((FinancialTransaction.direction == 'OUT', FinancialTransaction.amount), else_=0)).label('total_out')
        )
        
        if start_date:
            tx_agg_q = tx_agg_q.where(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            tx_agg_q = tx_agg_q.where(FinancialTransaction.transaction_date <= end_date)
            
        tx_agg_q = tx_agg_q.group_by(FinancialTransaction.transaction_type)
        tx_res = await db.execute(tx_agg_q)
        
        tx_nets = {}
        for row in tx_res.mappings():
            t_type = row['transaction_type']
            t_in = Decimal(row['total_in'] or '0.00')
            t_out = Decimal(row['total_out'] or '0.00')
            tx_nets[t_type] = {'in': t_in, 'out': t_out, 'net': t_in - t_out}

        def get_net(t_type: str) -> Decimal:
            return tx_nets.get(t_type, {}).get('net', Decimal('0.00'))

        # Operating Flows
        cash_from_sales = get_net('SALE')
        cash_to_suppliers = get_net('PURCHASE') # typically negative
        cash_for_expenses = get_net('EXPENSE')  # typically negative
        cash_for_payroll = get_net('PAYROLL')   # typically negative
        
        other_income_net = get_net('OTHER_INCOME')
        adjustments_net = get_net('ADJUSTMENT')
        other_operating_cash = other_income_net + adjustments_net
        
        # Investing Flows
        cash_for_assets = get_net('ASSET_PURCHASE') # typically negative
        
        # Financing Flows
        owner_investments = get_net('OWNER_INVESTMENT') # typically positive

        # Uncategorized (Failsafe)
        uncategorized_net = Decimal('0.00')
        handled_cf_types = {'SALE', 'PURCHASE', 'EXPENSE', 'PAYROLL', 'OTHER_INCOME', 'ADJUSTMENT', 'ASSET_PURCHASE', 'OWNER_INVESTMENT'}
        
        for t_type, flows in tx_nets.items():
            if t_type not in handled_cf_types:
                uncategorized_net += flows['net']

        return {
            "opening_balance": opening_balance,
            "cash_from_sales": cash_from_sales,
            "cash_to_suppliers": cash_to_suppliers,
            "cash_for_expenses": cash_for_expenses,
            "cash_for_payroll": cash_for_payroll,
            "other_operating_cash": other_operating_cash,
            "cash_for_assets": cash_for_assets,
            "owner_investments": owner_investments,
            "uncategorized_operating_cash": uncategorized_net
        }
