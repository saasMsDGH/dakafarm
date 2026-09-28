from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, and_, or_

from app.api.v1.reports.schemas.operations import (
    FarmOperationsReport, FinancialOverview, CashPosition,
    FarmOperations, CustomersSuppliers, InventorySummary,
    CriticalStockItem, AssetSummary, HRSummary, ExecutiveKPIs
)

from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.house import House
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.inventory.models.product import Product
from app.api.v1.assets.models.asset import Asset

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

        # -------------------------------------------------------------
        # 1. FINANCIAL OVERVIEW
        # -------------------------------------------------------------
        total_sales = Decimal((await db.execute(apply_dates(select(func.sum(Sale.total_amount)), Sale.sale_date))).scalar() or 0)
        total_purchases = Decimal((await db.execute(apply_dates(select(func.sum(Purchase.total_amount)), Purchase.purchase_date))).scalar() or 0)
        total_expenses = Decimal((await db.execute(apply_dates(select(func.sum(Expense.amount)), Expense.expense_date))).scalar() or 0)
        total_payroll = Decimal((await db.execute(apply_dates(select(func.sum(Payroll.net_salary)), Payroll.created_at))).scalar() or 0)

        total_cogs = total_purchases
        gross_profit = total_sales - total_cogs
        gross_margin_pct = (gross_profit / total_sales * 100) if total_sales > 0 else Decimal(0)
        gross_margin = f"{gross_margin_pct:.1f}%"

        total_operating_costs = total_expenses + total_payroll
        net_profit = gross_profit - total_operating_costs
        net_profit_margin_pct = (net_profit / total_sales * 100) if total_sales > 0 else Decimal(0)
        net_profit_margin = f"{net_profit_margin_pct:.1f}%"

        # -------------------------------------------------------------
        # 2. CASH POSITION & WORKING CAPITAL
        # -------------------------------------------------------------
        cash = Decimal(0)
        bank = Decimal(0)
        mobile_money = Decimal(0)

        acc_result = await db.execute(
            select(FinancialAccount.id, FinancialAccount.account_type, FinancialAccount.opening_balance)
            .where(FinancialAccount.is_active == True)
        )
        
        for acc_id, acc_type, opening_bal in acc_result:
            q_in = select(func.sum(FinancialTransaction.amount)).where(
                FinancialTransaction.account_id == acc_id, 
                FinancialTransaction.direction == 'IN'
            )
            q_out = select(func.sum(FinancialTransaction.amount)).where(
                FinancialTransaction.account_id == acc_id, 
                FinancialTransaction.direction == 'OUT'
            )
            
            t_in = Decimal((await db.execute(q_in)).scalar() or 0)
            t_out = Decimal((await db.execute(q_out)).scalar() or 0)
            
            bal = Decimal(opening_bal or 0) + t_in - t_out
            
            t = (acc_type or '').upper()
            if 'CASH' in t:
                cash += bal
            elif 'BANK' in t:
                bank += bal
            elif 'MOBILE' in t or 'M-PESA' in t or 'TIGO' in t or 'AIRTEL' in t:
                mobile_money += bal
            else:
                cash += bal

        total_available = cash + bank + mobile_money

        customer_out = Decimal((await db.execute(select(func.sum(Sale.total_amount - Sale.amount_paid)))).scalar() or 0)
        supplier_pay = Decimal((await db.execute(select(func.sum(Purchase.total_amount - Purchase.amount_paid)))).scalar() or 0)

        net_working_capital = total_available + customer_out - supplier_pay
        if total_available >= (supplier_pay * Decimal(1.2)) and total_available > 0:
            liquidity_status = "Optimal Liquidity"
        elif total_available >= supplier_pay:
            liquidity_status = "Adequate Reserves"
        elif total_available > 0:
            liquidity_status = "Moderate Strain"
        else:
            liquidity_status = "Severe Deficit"

        # -------------------------------------------------------------
        # 3. FARM & POULTRY OPERATIONS
        # -------------------------------------------------------------
        total_birds = int((await db.execute(select(func.sum(Flock.current_quantity)).where(func.upper(Flock.status) == 'ACTIVE'))).scalar() or 0)
        initial_birds = int((await db.execute(select(func.sum(Flock.initial_quantity)).where(func.upper(Flock.status) == 'ACTIVE'))).scalar() or 0)
        total_flocks = int((await db.execute(select(func.count(Flock.id)))).scalar() or 0)
        active_flocks = int((await db.execute(select(func.count(Flock.id)).where(func.upper(Flock.status) == 'ACTIVE'))).scalar() or 0)

        eggs_produced = int((await db.execute(apply_dates(select(func.sum(ProductionRecord.total_eggs)), ProductionRecord.record_date))).scalar() or 0)
        good_eggs = int((await db.execute(apply_dates(select(func.sum(ProductionRecord.good_eggs)), ProductionRecord.record_date))).scalar() or 0)
        damaged_eggs = int((await db.execute(apply_dates(select(func.sum(ProductionRecord.damaged_eggs)), ProductionRecord.record_date))).scalar() or 0)

        egg_breakage_rate = "0.0%"
        if eggs_produced > 0:
            egg_breakage_rate = f"{(damaged_eggs / eggs_produced) * 100:.1f}%"

        avg_laying_query = apply_dates(select(func.avg(ProductionRecord.laying_percentage)), ProductionRecord.record_date)
        avg_laying_val = (await db.execute(avg_laying_query)).scalar()
        average_laying_rate = f"{float(avg_laying_val):.1f}%" if avg_laying_val is not None else "0.0%"

        total_mortality = int((await db.execute(apply_dates(select(func.sum(MortalityRecord.quantity)), MortalityRecord.record_date))).scalar() or 0)
        mortality_rate = "0.0%"
        base_birds = initial_birds if initial_birds > 0 else total_birds
        if base_birds > 0:
            mortality_rate = f"{(total_mortality / base_birds) * 100:.1f}%"
            
        feed_used_kg = Decimal((await db.execute(apply_dates(select(func.sum(FeedRecord.quantity_used)), FeedRecord.record_date))).scalar() or 0)
        feed_cost = Decimal((await db.execute(apply_dates(select(func.sum(FeedRecord.total_cost)), FeedRecord.record_date))).scalar() or 0)
        feed_used_bags = int(round(feed_used_kg / 50)) if feed_used_kg > 0 else 0
        feed_used_str = f"{feed_used_kg:,.1f} Kg ({feed_used_bags:,} Bags)"

        vaccinations_due = int((await db.execute(select(func.count()).select_from(VaccinationRecord).where(VaccinationRecord.next_due_date <= func.current_date()))).scalar() or 0)
        low_stock = int((await db.execute(select(func.count()).select_from(Product).where(Product.current_stock <= Product.reorder_level))).scalar() or 0)

        active_houses = int((await db.execute(select(func.count(House.id)).where(House.status == True))).scalar() or 0)
        total_capacity = int((await db.execute(select(func.sum(House.capacity)).where(House.status == True))).scalar() or 0)
        capacity_utilization = "0.0%"
        if total_capacity > 0:
            capacity_utilization = f"{(total_birds / total_capacity) * 100:.1f}%"

        # -------------------------------------------------------------
        # 4. INVENTORY & SUPPLY CHAIN VALUATION
        # -------------------------------------------------------------
        total_skus = int((await db.execute(select(func.count(Product.id)).where(Product.is_active == True))).scalar() or 0)
        total_valuation = Decimal((await db.execute(select(func.sum(Product.current_stock * Product.unit_price)).where(Product.is_active == True))).scalar() or 0)
        low_stock_count = int((await db.execute(select(func.count(Product.id)).where(Product.is_active == True, Product.current_stock <= Product.reorder_level, Product.current_stock > 0))).scalar() or 0)
        out_of_stock_count = int((await db.execute(select(func.count(Product.id)).where(Product.is_active == True, Product.current_stock <= 0))).scalar() or 0)

        healthy_skus = max(0, total_skus - (low_stock_count + out_of_stock_count))
        stock_health_rate = f"{(healthy_skus / total_skus) * 100:.1f}%" if total_skus > 0 else "100.0%"

        critical_q = select(
            Product.name,
            Product.unit_of_measure,
            Product.current_stock,
            Product.reorder_level,
            Product.unit_price
        ).where(
            Product.is_active == True,
            Product.current_stock <= Product.reorder_level
        ).order_by(Product.current_stock.asc()).limit(5)

        critical_res = await db.execute(critical_q)
        critical_items = []
        for p_name, p_uom, p_stock, p_reorder, p_price in critical_res:
            stock_val = Decimal(p_stock or 0) * Decimal(p_price or 0)
            status_label = "OUT OF STOCK" if (p_stock or 0) <= 0 else "LOW STOCK"
            critical_items.append(
                CriticalStockItem(
                    name=p_name,
                    unit_of_measure=p_uom or "units",
                    current_stock=Decimal(p_stock or 0),
                    reorder_level=Decimal(p_reorder or 0),
                    unit_price=Decimal(p_price or 0),
                    stock_value=stock_val,
                    status=status_label
                )
            )

        # -------------------------------------------------------------
        # 5. FIXED ASSETS & INFRASTRUCTURE
        # -------------------------------------------------------------
        total_assets_count = int((await db.execute(select(func.count(Asset.id)).where(func.upper(Asset.status) != 'DISPOSED'))).scalar() or 0)
        total_quantity = int((await db.execute(select(func.sum(Asset.quantity)).where(func.upper(Asset.status) != 'DISPOSED'))).scalar() or 0)
        total_asset_cost = Decimal((await db.execute(select(func.sum(Asset.cost_price * Asset.quantity)).where(func.upper(Asset.status) != 'DISPOSED'))).scalar() or 0)
        total_paid_asset = Decimal((await db.execute(select(func.sum(Asset.amount_paid)).where(func.upper(Asset.status) != 'DISPOSED'))).scalar() or 0)
        total_payable_asset = max(Decimal(0), total_asset_cost - total_paid_asset)

        good_condition_count = int((await db.execute(select(func.count(Asset.id)).where(func.upper(Asset.status) != 'DISPOSED', func.upper(Asset.condition).in_(['GOOD', 'NEW', 'EXCELLENT'])))).scalar() or 0)
        fair_or_poor_count = int((await db.execute(select(func.count(Asset.id)).where(func.upper(Asset.status) != 'DISPOSED', func.upper(Asset.condition).in_(['FAIR', 'POOR', 'DAMAGED'])))).scalar() or 0)
        in_maintenance_count = int((await db.execute(select(func.count(Asset.id)).where(func.upper(Asset.status) == 'MAINTENANCE'))).scalar() or 0)

        # -------------------------------------------------------------
        # 6. HUMAN RESOURCES & PAYROLL
        # -------------------------------------------------------------
        total_staff = int((await db.execute(select(func.count(Employee.id)))).scalar() or 0)
        active_staff = int((await db.execute(select(func.count(Employee.id)).where(Employee.status == True))).scalar() or 0)

        hr_query = apply_dates(
            select(
                func.sum(Payroll.basic_salary),
                func.sum(Payroll.allowances),
                func.sum(Payroll.deductions),
                func.sum(Payroll.net_salary),
                func.sum(Payroll.amount_paid)
            ),
            Payroll.created_at
        )
        hr_res = (await db.execute(hr_query)).first()
        total_basic = Decimal(hr_res[0] or 0) if hr_res else Decimal(0)
        total_allow = Decimal(hr_res[1] or 0) if hr_res else Decimal(0)
        total_ded = Decimal(hr_res[2] or 0) if hr_res else Decimal(0)
        total_net_payroll = Decimal(hr_res[3] or 0) if hr_res else Decimal(0)
        paid_payroll = Decimal(hr_res[4] or 0) if hr_res else Decimal(0)
        pending_payroll = max(Decimal(0), total_net_payroll - paid_payroll)

        # -------------------------------------------------------------
        # 7. CUSTOMERS & SUPPLIERS
        # -------------------------------------------------------------
        active_customers = int((await db.execute(select(func.count()).select_from(Customer))).scalar() or 0)
        active_suppliers = int((await db.execute(select(func.count()).select_from(Supplier))).scalar() or 0)

        # -------------------------------------------------------------
        # 8. EXECUTIVE KPIS & SMART INTELLIGENCE
        # -------------------------------------------------------------
        if net_profit > 0:
            profit_margin_status = f"Strong Surplus ({net_profit_margin})" if net_profit_margin_pct >= 20 else f"Moderate Profit ({net_profit_margin})"
        elif net_profit == 0:
            profit_margin_status = "Break-Even (0.0%)"
        else:
            profit_margin_status = f"Deficit Warning ({net_profit_margin})"

        if net_working_capital > 0 and total_available >= supplier_pay:
            cash_flow_health = "Strong Liquidity"
        elif total_available > 0:
            cash_flow_health = "Constrained Liquidity"
        else:
            cash_flow_health = "Deficit / Risk"

        lay_f = float(avg_laying_val) if avg_laying_val is not None else 0.0
        if lay_f >= 80.0:
            laying_performance = f"Peak Yield ({lay_f:.1f}%)"
        elif lay_f >= 65.0:
            laying_performance = f"Normal Range ({lay_f:.1f}%)"
        elif lay_f > 0:
            laying_performance = f"Sub-Optimal ({lay_f:.1f}%)"
        else:
            laying_performance = "No Active Yield Data"

        mort_pct = (total_mortality / base_birds * 100) if base_birds > 0 else 0.0
        if mort_pct <= 2.5:
            mortality_alert_level = f"Optimal (<2.5%)"
        elif mort_pct <= 5.0:
            mortality_alert_level = f"Elevated Risk ({mort_pct:.1f}%)"
        else:
            mortality_alert_level = f"Critical Alert ({mort_pct:.1f}%)"

        if out_of_stock_count > 0:
            inventory_risk = f"Stockouts Detected ({out_of_stock_count} SKUs)"
        elif low_stock_count > 0:
            inventory_risk = f"Reorder Required ({low_stock_count} SKUs)"
        else:
            inventory_risk = "Inventory Optimum"

        report_ref = f"AF-OPR-{datetime.utcnow().strftime('%Y%m%d')}-{datetime.utcnow().strftime('%H%M')}"

        return FarmOperationsReport(
            period_start=date_from,
            period_end=date_to,
            generated_on=datetime.utcnow(),
            report_reference=report_ref,
            financial_overview=FinancialOverview(
                total_sales=total_sales,
                total_purchases=total_purchases,
                total_cogs=total_cogs,
                gross_profit=gross_profit,
                gross_margin=gross_margin,
                total_expenses=total_expenses,
                total_payroll=total_payroll,
                total_operating_costs=total_operating_costs,
                net_profit=net_profit,
                net_profit_margin=net_profit_margin
            ),
            cash_position=CashPosition(
                cash=cash,
                bank=bank,
                mobile_money=mobile_money,
                total_available=total_available,
                customer_outstanding=customer_out,
                supplier_payable=supplier_pay,
                net_working_capital=net_working_capital,
                liquidity_status=liquidity_status
            ),
            farm_operations=FarmOperations(
                total_flocks=total_flocks,
                active_flocks=active_flocks,
                total_birds=total_birds,
                initial_birds=initial_birds,
                total_mortality=total_mortality,
                mortality_rate=mortality_rate,
                eggs_produced=eggs_produced,
                good_eggs=good_eggs,
                damaged_eggs=damaged_eggs,
                egg_breakage_rate=egg_breakage_rate,
                average_laying_rate=average_laying_rate,
                feed_used=feed_used_str,
                feed_used_kg=feed_used_kg,
                feed_cost=feed_cost,
                vaccinations_due=vaccinations_due,
                active_houses=active_houses,
                total_capacity=total_capacity,
                capacity_utilization=capacity_utilization,
                low_stock_items=low_stock
            ),
            inventory_summary=InventorySummary(
                total_skus=total_skus,
                total_valuation=total_valuation,
                low_stock_count=low_stock_count,
                out_of_stock_count=out_of_stock_count,
                stock_health_rate=stock_health_rate,
                critical_items=critical_items
            ),
            asset_summary=AssetSummary(
                total_assets_count=total_assets_count,
                total_quantity=total_quantity,
                total_asset_cost=total_asset_cost,
                total_paid=total_paid_asset,
                total_payable=total_payable_asset,
                good_condition_count=good_condition_count,
                fair_or_poor_count=fair_or_poor_count,
                in_maintenance_count=in_maintenance_count
            ),
            hr_summary=HRSummary(
                total_staff=total_staff,
                active_staff=active_staff,
                total_basic_salary=total_basic,
                total_allowances=total_allow,
                total_deductions=total_ded,
                net_payroll_liability=total_net_payroll,
                paid_payroll=paid_payroll,
                pending_payroll=pending_payroll
            ),
            customers_suppliers=CustomersSuppliers(
                customer_outstanding=customer_out,
                supplier_payable=supplier_pay,
                active_customers=active_customers,
                active_suppliers=active_suppliers
            ),
            executive_kpis=ExecutiveKPIs(
                profit_margin_status=profit_margin_status,
                cash_flow_health=cash_flow_health,
                laying_performance=laying_performance,
                mortality_alert_level=mortality_alert_level,
                inventory_risk=inventory_risk
            )
        )
