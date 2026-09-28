from typing import Tuple, List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.finance.models.account import FinancialAccount

class TrialBalanceRepo:
    @staticmethod
    async def generate_trial_balance(db: AsyncSession, as_of_date: Optional[datetime] = None) -> Tuple[List[dict], Decimal, Decimal]:
        # If no date is provided, use current UTC time
        if not as_of_date:
            as_of_date = datetime.utcnow()

        # 1. Accounts Opening Balances (Equity CR)
        accounts_agg = await db.execute(
            select(func.sum(FinancialAccount.opening_balance))
            .where(FinancialAccount.created_at <= as_of_date)
        )
        total_opening_balance = Decimal(accounts_agg.scalar() or '0.00')

        # 2. Sales (Revenue CR)
        sales_agg = await db.execute(
            select(func.sum(Sale.total_amount))
            .where(Sale.sale_date <= as_of_date)
        )
        total_sales = Decimal(sales_agg.scalar() or '0.00')

        # 3. Purchases (Expense DR)
        purchases_agg = await db.execute(
            select(func.sum(Purchase.total_amount))
            .where(Purchase.purchase_date <= as_of_date)
        )
        total_purchases = Decimal(purchases_agg.scalar() or '0.00')

        # 4. Transactions Aggregation grouped by type
        ft_agg_query = select(
            FinancialTransaction.transaction_type,
            func.sum(case((FinancialTransaction.direction == 'IN', FinancialTransaction.amount), else_=0)).label('total_in'),
            func.sum(case((FinancialTransaction.direction == 'OUT', FinancialTransaction.amount), else_=0)).label('total_out')
        ).where(FinancialTransaction.transaction_date <= as_of_date).group_by(FinancialTransaction.transaction_type)

        ft_res = await db.execute(ft_agg_query)
        
        # We will build a dictionary of net movements per transaction type
        tx_nets = {}
        total_in = Decimal('0.00')
        total_out = Decimal('0.00')
        
        for row in ft_res.mappings():
            t_type = row['transaction_type']
            t_in = Decimal(row['total_in'] or '0.00')
            t_out = Decimal(row['total_out'] or '0.00')
            total_in += t_in
            total_out += t_out
            tx_nets[t_type] = {'in': t_in, 'out': t_out}

        # Helper to get specific type flows
        def get_flow(t_type):
            return tx_nets.get(t_type, {'in': Decimal('0.00'), 'out': Decimal('0.00')})

        sale_flows = get_flow('SALE')
        sale_payments_in = sale_flows['in']
        sale_payments_out = sale_flows['out']
        
        purchase_flows = get_flow('PURCHASE')
        purchase_payments_out = purchase_flows['out']
        purchase_payments_in = purchase_flows['in']

        # Complex Balances
        cash_balance = total_opening_balance + total_in - total_out
        accounts_receivable = total_sales - sale_payments_in + sale_payments_out
        accounts_payable = total_purchases - purchase_payments_out + purchase_payments_in

        # Collect Entries
        entries = []

        # DEBITS (Assets & Expenses)
        if cash_balance > 0:
            entries.append({"account_name": "Cash & Bank Balances", "debit": cash_balance, "credit": Decimal('0.00')})
        elif cash_balance < 0:
            # Overdraft is a liability (CR)
            entries.append({"account_name": "Cash & Bank Balances (Overdraft)", "debit": Decimal('0.00'), "credit": abs(cash_balance)})

        if accounts_receivable > 0:
            entries.append({"account_name": "Accounts Receivable", "debit": accounts_receivable, "credit": Decimal('0.00')})
        elif accounts_receivable < 0:
            entries.append({"account_name": "Accounts Receivable (Overpaid)", "debit": Decimal('0.00'), "credit": abs(accounts_receivable)})
            
        if total_purchases > 0:
            entries.append({"account_name": "Purchases (COGS)", "debit": total_purchases, "credit": Decimal('0.00')})
            
        exp_flows = get_flow('EXPENSE')
        direct_expenses_net = exp_flows['out'] - exp_flows['in']
        if direct_expenses_net > 0:
            entries.append({"account_name": "Direct Expenses", "debit": direct_expenses_net, "credit": Decimal('0.00')})
        elif direct_expenses_net < 0:
            entries.append({"account_name": "Direct Expenses (Recovered)", "debit": Decimal('0.00'), "credit": abs(direct_expenses_net)})
            
        payroll_flows = get_flow('PAYROLL')
        payroll_net = payroll_flows['out'] - payroll_flows['in']
        if payroll_net > 0:
            entries.append({"account_name": "Payroll Expenses", "debit": payroll_net, "credit": Decimal('0.00')})
        elif payroll_net < 0:
            entries.append({"account_name": "Payroll Expenses (Recovered)", "debit": Decimal('0.00'), "credit": abs(payroll_net)})
            
        asset_flows = get_flow('ASSET_PURCHASE')
        asset_net = asset_flows['out'] - asset_flows['in']
        if asset_net > 0:
            entries.append({"account_name": "Fixed Assets", "debit": asset_net, "credit": Decimal('0.00')})
        elif asset_net < 0:
            entries.append({"account_name": "Fixed Assets (Disposed)", "debit": Decimal('0.00'), "credit": abs(asset_net)})
            
        adj_flows = get_flow('ADJUSTMENT')
        adj_out = adj_flows['out']
        adj_in = adj_flows['in']
        if adj_out > 0:
            entries.append({"account_name": "Negative Adjustments (Losses)", "debit": adj_out, "credit": Decimal('0.00')})
        if adj_in > 0:
            entries.append({"account_name": "Positive Adjustments (Gains)", "debit": Decimal('0.00'), "credit": adj_in})

        # CREDITS (Liabilities, Equity, Revenue)
        if accounts_payable > 0:
            entries.append({"account_name": "Accounts Payable", "debit": Decimal('0.00'), "credit": accounts_payable})
        elif accounts_payable < 0:
            entries.append({"account_name": "Accounts Payable (Prepaid)", "debit": abs(accounts_payable), "credit": Decimal('0.00')})
            
        if total_sales > 0:
            entries.append({"account_name": "Sales Revenue", "debit": Decimal('0.00'), "credit": total_sales})
            
        income_flows = get_flow('OTHER_INCOME')
        income_net = income_flows['in'] - income_flows['out']
        if income_net > 0:
            entries.append({"account_name": "Other Income", "debit": Decimal('0.00'), "credit": income_net})
        elif income_net < 0:
            entries.append({"account_name": "Other Income (Refunded)", "debit": abs(income_net), "credit": Decimal('0.00')})
            
        equity_flows = get_flow('OWNER_INVESTMENT')
        equity_net = equity_flows['in'] - equity_flows['out']
        if equity_net > 0:
            entries.append({"account_name": "Owner Investment (Equity)", "debit": Decimal('0.00'), "credit": equity_net})
        elif equity_net < 0:
            entries.append({"account_name": "Owner Drawing (Equity)", "debit": abs(equity_net), "credit": Decimal('0.00')})
            
        if total_opening_balance > 0:
            entries.append({"account_name": "Account Opening Balances (Equity)", "debit": Decimal('0.00'), "credit": total_opening_balance})
        
        handled_types = {'SALE', 'PURCHASE', 'EXPENSE', 'PAYROLL', 'ASSET_PURCHASE', 'ADJUSTMENT', 'OTHER_INCOME', 'OWNER_INVESTMENT'}
        for t_type, flows in tx_nets.items():
            if t_type not in handled_types:
                net = flows['in'] - flows['out']
                if net > 0:
                    entries.append({"account_name": f"Uncategorized Income ({t_type})", "debit": Decimal('0.00'), "credit": net})
                elif net < 0:
                    entries.append({"account_name": f"Uncategorized Expense ({t_type})", "debit": abs(net), "credit": Decimal('0.00')})

        # Calculate Totals
        total_debits = sum(e["debit"] for e in entries)
        total_credits = sum(e["credit"] for e in entries)

        return entries, total_debits, total_credits
