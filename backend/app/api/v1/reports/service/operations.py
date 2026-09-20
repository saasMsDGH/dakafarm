from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.v1.reports.schemas.operations import (
    FarmOperationsReport, FlockSummary, HealthSummary, ProductionSummary, 
    HRSummary, FinanceSummary, AssetsSummary
)

from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.medication_record import MedicationRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.expense import Expense
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

        # 1. FLOCKS & BIRDS
        active_flocks_count = (await db.execute(select(func.count()).select_from(Flock).where(Flock.status == 'ACTIVE'))).scalar() or 0
        total_birds = (await db.execute(select(func.sum(Flock.current_quantity)).where(Flock.status == 'ACTIVE'))).scalar() or 0
        
        q_mort = apply_dates(select(func.sum(MortalityRecord.quantity)), MortalityRecord.record_date)
        total_mortality = (await db.execute(q_mort)).scalar() or 0

        # 2. HEALTH
        q_med = apply_dates(select(func.sum(MedicationRecord.total_cost)), MedicationRecord.record_date)
        med_cost = Decimal((await db.execute(q_med)).scalar() or 0)
        
        q_vac = apply_dates(select(func.sum(VaccinationRecord.total_cost)), VaccinationRecord.record_date)
        vac_cost = Decimal((await db.execute(q_vac)).scalar() or 0)

        # 3. PRODUCTION
        q_prod = apply_dates(select(func.sum(ProductionRecord.total_eggs)), ProductionRecord.record_date)
        total_prod = Decimal((await db.execute(q_prod)).scalar() or 0)

        # 4. HR
        total_emp = (await db.execute(select(func.count()).select_from(Employee).where(Employee.status == True))).scalar() or 0
        q_pay = select(func.sum(Payroll.net_salary)) # Payroll date filtering might be by payment date, let's keep it simple for now
        total_payroll = Decimal((await db.execute(q_pay)).scalar() or 0)

        # 5. ASSETS
        total_assets = (await db.execute(select(func.count()).select_from(Asset).where(Asset.status == 'Active'))).scalar() or 0
        asset_val = Decimal((await db.execute(select(func.sum(Asset.cost_price)).where(Asset.status == 'Active'))).scalar() or 0)

        # 6. FINANCE
        q_rev = apply_dates(select(func.sum(Sale.total_amount)), Sale.sale_date)
        revenue = Decimal((await db.execute(q_rev)).scalar() or 0)
        
        q_exp1 = apply_dates(select(func.sum(Expense.amount)), Expense.expense_date)
        expenses_general = Decimal((await db.execute(q_exp1)).scalar() or 0)
        
        q_exp2 = apply_dates(select(func.sum(Purchase.total_amount)), Purchase.purchase_date)
        purchases = Decimal((await db.execute(q_exp2)).scalar() or 0)
        
        total_expenses = expenses_general + purchases + total_payroll

        return FarmOperationsReport(
            period_start=date_from,
            period_end=date_to,
            flocks=FlockSummary(
                total_birds=int(total_birds),
                active_flocks=int(active_flocks_count),
                total_mortality=int(total_mortality),
                sick_birds=0 # Placeholder unless there's a sick birds tracking mechanism
            ),
            health=HealthSummary(
                medication_cost=med_cost,
                vaccines_used=vac_cost
            ),
            production=ProductionSummary(
                total_quantity=total_prod
            ),
            hr=HRSummary(
                total_employees=int(total_emp),
                payroll_total=total_payroll
            ),
            assets=AssetsSummary(
                total_active_assets=int(total_assets),
                asset_value=asset_val
            ),
            finance=FinanceSummary(
                revenue=revenue,
                expenses=total_expenses,
                net_profit=revenue - total_expenses
            )
        )
