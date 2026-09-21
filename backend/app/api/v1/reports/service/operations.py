from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case

from app.api.v1.reports.schemas.operations import (
    FarmOperationsReport, FinancialOverview, CashPosition,
    FarmOperations, CustomersSuppliers
)

from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.inventory.models.product import Product

class OperationsReportService:

    @staticmethod
    async def get_master_summary(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> FarmOperationsReport:

        def apply_dates(q, date_col):
            if date_from:
                q = q.where(date_col >= date_from)
            if date_to:
                q = q.where(date_col <= date_to)
            return q

        # --- FINANCIAL OVERVIEW ---
        total_sales = Decimal((await db.execute(apply_dates(select(func.sum(Sale.total_amount)), Sale.sale_date))).scalar() or 0)
        total_purchases = Decimal((await db.execute(apply_dates(select(func.sum(Purchase.total_amount)), Purchase.purchase_date))).scalar() or 0)
        total_expenses = Decimal((await db.execute(apply_dates(select(func.sum(Expense.amount)), Expense.expense_date))).scalar() or 0)
        total_payroll = Decimal((await db.execute(select(func.sum(Payroll.net_salary)))).scalar() or 0)
        
        net_profit = total_sales - (total_purchases + total_expenses + total_payroll)

        # --- CASH POSITION ---
        cash = Decimal(0)
        bank = Decimal(0)
        mobile_money = Decimal(0)

        # Get accounts
        acc_result = await db.execute(select(FinancialAccount.id, FinancialAccount.account_type, FinancialAccount.opening_balance).where(FinancialAccount.is_active == True))
        
        for acc_id, acc_type, opening_bal in acc_result:
            # sum transactions
            q_in = select(func.sum(FinancialTransaction.amount)).where(FinancialTransaction.account_id == acc_id, FinancialTransaction.direction == 'IN')
            q_out = select(func.sum(FinancialTransaction.amount)).where(FinancialTransaction.account_id == acc_id, FinancialTransaction.direction == 'OUT')
            
            t_in = Decimal((await db.execute(q_in)).scalar() or 0)
            t_out = Decimal((await db.execute(q_out)).scalar() or 0)
            
            bal = Decimal(opening_bal or 0) + t_in - t_out
            
            t = acc_type.upper()
            if 'CASH' in t:
                cash += bal
            elif 'BANK' in t:
                bank += bal
            elif 'MOBILE' in t or 'M-PESA' in t:
                mobile_money += bal
            else:
                cash += bal

        total_available = cash + bank + mobile_money

        # --- FARM OPERATIONS ---
        total_birds = int((await db.execute(select(func.sum(Flock.current_quantity)).where(Flock.status == 'ACTIVE'))).scalar() or 0)
        initial_birds = int((await db.execute(select(func.sum(Flock.initial_quantity)).where(Flock.status == 'ACTIVE'))).scalar() or 0)
        eggs_produced = int((await db.execute(apply_dates(select(func.sum(ProductionRecord.total_eggs)), ProductionRecord.record_date))).scalar() or 0)
        
        total_mortality = int((await db.execute(apply_dates(select(func.sum(MortalityRecord.quantity)), MortalityRecord.record_date))).scalar() or 0)
        mortality_rate = "0.0%"
        if initial_birds > 0:
            mortality_rate = f"{(total_mortality / initial_birds) * 100:.1f}%"
            
        feed_used_kg = int((await db.execute(apply_dates(select(func.sum(FeedRecord.quantity_used)), FeedRecord.record_date))).scalar() or 0)
        feed_used_str = f"{feed_used_kg} Bags"

        vaccinations_due = int((await db.execute(select(func.count()).select_from(VaccinationRecord).where(VaccinationRecord.next_due_date <= func.current_date()))).scalar() or 0)
        low_stock = int((await db.execute(select(func.count()).select_from(Product).where(Product.current_stock <= Product.reorder_level))).scalar() or 0)

        # --- CUSTOMERS & SUPPLIERS ---
        customer_out = Decimal((await db.execute(select(func.sum(Sale.total_amount - Sale.amount_paid)))).scalar() or 0)
        supplier_pay = Decimal((await db.execute(select(func.sum(Purchase.total_amount - Purchase.amount_paid)))).scalar() or 0)
        
        active_customers = int((await db.execute(select(func.count()).select_from(Customer))).scalar() or 0)
        active_suppliers = int((await db.execute(select(func.count()).select_from(Supplier))).scalar() or 0)

        return FarmOperationsReport(
            period_start=date_from,
            period_end=date_to,
            generated_on=datetime.utcnow(),
            financial_overview=FinancialOverview(
                total_sales=total_sales,
                total_purchases=total_purchases,
                total_expenses=total_expenses,
                total_payroll=total_payroll,
                net_profit=net_profit
            ),
            cash_position=CashPosition(
                cash=cash,
                bank=bank,
                mobile_money=mobile_money,
                total_available=total_available
            ),
            farm_operations=FarmOperations(
                total_birds=total_birds,
                eggs_produced=eggs_produced,
                mortality_rate=mortality_rate,
                feed_used=feed_used_str,
                vaccinations_due=vaccinations_due,
                low_stock_items=low_stock
            ),
            customers_suppliers=CustomersSuppliers(
                customer_outstanding=customer_out,
                supplier_payable=supplier_pay,
                active_customers=active_customers,
                active_suppliers=active_suppliers
            )
        )
