from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount

class BalanceSheetRepo:
    @staticmethod
    async def generate_balance_sheet(db: AsyncSession, as_of_date: Optional[datetime] = None) -> Dict:
        # 1. Accounts Opening Balance
        acct_q = select(func.sum(FinancialAccount.opening_balance))
        if as_of_date:
            acct_q = acct_q.where(FinancialAccount.created_at <= as_of_date)
        acct_res = await db.execute(acct_q)
        total_opening_balance = Decimal(acct_res.scalar() or '0.00')

        # 2. Sales (Invoices)
        sales_q = select(func.sum(Sale.total_amount))
        if as_of_date:
            sales_q = sales_q.where(Sale.sale_date <= as_of_date)
        sales_res = await db.execute(sales_q)
        total_sales_invoiced = Decimal(sales_res.scalar() or '0.00')

        # 3. Purchases (Invoices)
        purch_q = select(func.sum(Purchase.total_amount))
        if as_of_date:
            purch_q = purch_q.where(Purchase.purchase_date <= as_of_date)
        purch_res = await db.execute(purch_q)
        total_purchases_invoiced = Decimal(purch_res.scalar() or '0.00')

        # 4. Financial Transactions
        tx_agg_q = select(
            FinancialTransaction.transaction_type,
            func.sum(case((FinancialTransaction.direction == 'IN', FinancialTransaction.amount), else_=0)).label('total_in'),
            func.sum(case((FinancialTransaction.direction == 'OUT', FinancialTransaction.amount), else_=0)).label('total_out')
        )
        if as_of_date:
            tx_agg_q = tx_agg_q.where(FinancialTransaction.transaction_date <= as_of_date)
            
        tx_agg_q = tx_agg_q.group_by(FinancialTransaction.transaction_type)
        tx_res = await db.execute(tx_agg_q)
        
        tx_nets = {}
        total_cash_in = Decimal('0.00')
        total_cash_out = Decimal('0.00')
        
        for row in tx_res.mappings():
            t_type = row['transaction_type']
            t_in = Decimal(row['total_in'] or '0.00')
            t_out = Decimal(row['total_out'] or '0.00')
            tx_nets[t_type] = {'in': t_in, 'out': t_out}
            total_cash_in += t_in
            total_cash_out += t_out

        def get_flow(t_type: str) -> Dict[str, Decimal]:
            return tx_nets.get(t_type, {'in': Decimal('0.00'), 'out': Decimal('0.00')})

        # --- ASSETS ---
        cash_and_bank = total_opening_balance + total_cash_in - total_cash_out
        
        sale_flows = get_flow('SALE')
        net_ar = total_sales_invoiced - sale_flows['in'] + sale_flows['out']
        accounts_receivable = max(Decimal('0.00'), net_ar)
        unearned_revenue = abs(min(Decimal('0.00'), net_ar))
        
        purch_flows = get_flow('PURCHASE')
        net_ap = total_purchases_invoiced - purch_flows['out'] + purch_flows['in']
        accounts_payable = max(Decimal('0.00'), net_ap)
        prepaid_purchases = abs(min(Decimal('0.00'), net_ap))
        
        asset_flows = get_flow('ASSET_PURCHASE')
        fixed_assets = asset_flows['out'] - asset_flows['in']

        # --- EQUITY (Owner Capital) ---
        owner_flows = get_flow('OWNER_INVESTMENT')
        owner_capital = total_opening_balance + (owner_flows['in'] - owner_flows['out'])

        # --- EQUITY (Retained Earnings) ---
        # Revenue
        other_inc_flows = get_flow('OTHER_INCOME')
        adj_flows = get_flow('ADJUSTMENT')
        total_revenue = total_sales_invoiced + (other_inc_flows['in'] - other_inc_flows['out']) + adj_flows['in']
        
        # Expenses
        exp_flows = get_flow('EXPENSE')
        pay_flows = get_flow('PAYROLL')
        total_expenses = total_purchases_invoiced + (exp_flows['out'] - exp_flows['in']) + (pay_flows['out'] - pay_flows['in']) + adj_flows['out']
        
        # Uncategorized
        uncat_net = Decimal('0.00')
        handled = {'SALE', 'PURCHASE', 'EXPENSE', 'PAYROLL', 'ASSET_PURCHASE', 'ADJUSTMENT', 'OTHER_INCOME', 'OWNER_INVESTMENT'}
        for t_type, flows in tx_nets.items():
            if t_type not in handled:
                uncat_net += flows['in'] - flows['out']
                
        retained_earnings = total_revenue - total_expenses + uncat_net

        return {
            "cash_and_bank": cash_and_bank,
            "accounts_receivable": accounts_receivable,
            "prepaid_purchases": prepaid_purchases,
            "fixed_assets": fixed_assets,
            
            "accounts_payable": accounts_payable,
            "unearned_revenue": unearned_revenue,
            
            "owner_capital": owner_capital,
            "retained_earnings": retained_earnings
        }
