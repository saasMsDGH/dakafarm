from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.finance.models.transaction import FinancialTransaction

class PnLRepo:
    @staticmethod
    async def generate_pnl(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        # 1. Sales (Operating Revenue)
        sales_q = select(func.sum(Sale.total_amount))
        if start_date:
            sales_q = sales_q.where(Sale.sale_date >= start_date)
        if end_date:
            sales_q = sales_q.where(Sale.sale_date <= end_date)
        
        sales_agg = await db.execute(sales_q)
        total_sales = Decimal(sales_agg.scalar() or '0.00')

        # 2. Purchases (COGS)
        purchases_q = select(func.sum(Purchase.total_amount))
        if start_date:
            purchases_q = purchases_q.where(Purchase.purchase_date >= start_date)
        if end_date:
            purchases_q = purchases_q.where(Purchase.purchase_date <= end_date)
            
        purchases_agg = await db.execute(purchases_q)
        total_purchases = Decimal(purchases_agg.scalar() or '0.00')

        # 3. Transactions Aggregation
        # We exclude BALANCE SHEET transaction types from the P&L entirely.
        # Included: EXPENSE, PAYROLL, OTHER_INCOME, ADJUSTMENT + any unrecognized anomalies.
        # Excluded: SALE (covered by Sales invoice), PURCHASE (covered by Purchase invoice), 
        #           ASSET_PURCHASE (Capitalized, not expensed), OWNER_INVESTMENT (Equity).
        
        excluded_types = ['SALE', 'PURCHASE', 'ASSET_PURCHASE', 'OWNER_INVESTMENT']
        
        ft_agg_q = select(
            FinancialTransaction.transaction_type,
            func.sum(case((FinancialTransaction.direction == 'IN', FinancialTransaction.amount), else_=0)).label('total_in'),
            func.sum(case((FinancialTransaction.direction == 'OUT', FinancialTransaction.amount), else_=0)).label('total_out')
        ).where(FinancialTransaction.transaction_type.notin_(excluded_types))
        
        if start_date:
            ft_agg_q = ft_agg_q.where(FinancialTransaction.transaction_date >= start_date)
        if end_date:
            ft_agg_q = ft_agg_q.where(FinancialTransaction.transaction_date <= end_date)
            
        ft_agg_q = ft_agg_q.group_by(FinancialTransaction.transaction_type)
        ft_res = await db.execute(ft_agg_q)
        
        tx_nets = {}
        for row in ft_res.mappings():
            t_type = row['transaction_type']
            t_in = Decimal(row['total_in'] or '0.00')
            t_out = Decimal(row['total_out'] or '0.00')
            tx_nets[t_type] = {'in': t_in, 'out': t_out}

        def get_flow(t_type: str) -> Dict[str, Decimal]:
            return tx_nets.get(t_type, {'in': Decimal('0.00'), 'out': Decimal('0.00')})

        # Calculate OPEX
        exp_flows = get_flow('EXPENSE')
        direct_expenses = exp_flows['out'] - exp_flows['in']  # Net expense
        
        payroll_flows = get_flow('PAYROLL')
        payroll_expenses = payroll_flows['out'] - payroll_flows['in']
        
        adj_flows = get_flow('ADJUSTMENT')
        negative_adjustments = adj_flows['out']  # Losses
        positive_adjustments = adj_flows['in']   # Gains
        
        # Calculate Non-Operating
        inc_flows = get_flow('OTHER_INCOME')
        other_income = inc_flows['in'] - inc_flows['out']
        
        # Uncategorized (Anomalies)
        uncategorized_in = Decimal('0.00')
        uncategorized_out = Decimal('0.00')
        handled_pnl_types = {'EXPENSE', 'PAYROLL', 'ADJUSTMENT', 'OTHER_INCOME'}
        
        for t_type, flows in tx_nets.items():
            if t_type not in handled_pnl_types:
                net = flows['in'] - flows['out']
                if net > 0:
                    uncategorized_in += net
                elif net < 0:
                    uncategorized_out += abs(net)

        return {
            "sales": total_sales,
            "purchases": total_purchases,
            "direct_expenses": direct_expenses,
            "payroll": payroll_expenses,
            "negative_adjustments": negative_adjustments,
            "other_income": other_income,
            "positive_adjustments": positive_adjustments,
            "uncategorized_income": uncategorized_in,
            "uncategorized_expense": uncategorized_out
        }
