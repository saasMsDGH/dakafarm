from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.house import House
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.models.medication_record import MedicationRecord
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.inventory.models.product import Product
from app.shared.pagination import PaginationParams


class FarmReportRepo:

    @staticmethod
    async def production_detail(db, params, flock_id=None, house_id=None, date_from=None, date_to=None):
        q = (
            select(ProductionRecord, Flock.flock_code, House.name.label('house_name'))
            .join(Flock, ProductionRecord.flock_id == Flock.id)
            .join(House, Flock.house_id == House.id)
        )
        if flock_id: q = q.where(ProductionRecord.flock_id == flock_id)
        if house_id: q = q.where(Flock.house_id == house_id)
        if date_from: q = q.where(ProductionRecord.record_date >= date_from)
        if date_to: q = q.where(ProductionRecord.record_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        totals_q = select(
            func.coalesce(func.sum(ProductionRecord.total_eggs), 0),
            func.coalesce(func.sum(ProductionRecord.good_eggs), 0),
            func.coalesce(func.sum(ProductionRecord.damaged_eggs), 0),
            func.avg(ProductionRecord.laying_percentage),
        )
        if flock_id: totals_q = totals_q.where(ProductionRecord.flock_id == flock_id)
        if date_from: totals_q = totals_q.where(ProductionRecord.record_date >= date_from)
        if date_to: totals_q = totals_q.where(ProductionRecord.record_date <= date_to)
        t = (await db.execute(totals_q)).one()
        q = q.order_by(ProductionRecord.record_date.desc())
        q = q.offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        items = []
        for row in rows:
            pr = row[0]
            items.append({
                'id': pr.id, 'record_date': pr.record_date, 'flock_code': row[1], 'house_name': row[2],
                'total_birds': pr.total_birds, 'total_eggs': pr.total_eggs, 'damaged_eggs': pr.damaged_eggs,
                'good_eggs': pr.good_eggs, 'laying_percentage': pr.laying_percentage, 'recorded_by': pr.recorded_by,
            })
        return items, total, int(t[0] or 0), int(t[1] or 0), int(t[2] or 0), t[3]

    @staticmethod
    async def production_by_flock(db, date_from=None, date_to=None):
        q = (
            select(
                Flock.id.label('flock_id'),
                Flock.flock_code,
                House.name.label('house_name'),
                Flock.current_quantity.label('bird_population'),
                func.coalesce(func.sum(ProductionRecord.total_eggs), 0).label('total_eggs'),
                func.coalesce(func.sum(ProductionRecord.damaged_eggs), 0).label('damaged_eggs'),
                func.coalesce(func.sum(ProductionRecord.good_eggs), 0).label('good_eggs'),
                func.avg(ProductionRecord.laying_percentage).label('avg_laying_pct'),
            )
            .join(ProductionRecord, ProductionRecord.flock_id == Flock.id)
            .join(House, Flock.house_id == House.id)
        )
        if date_from: q = q.where(ProductionRecord.record_date >= date_from)
        if date_to: q = q.where(ProductionRecord.record_date <= date_to)
        q = q.group_by(Flock.id, Flock.flock_code, House.name, Flock.current_quantity)
        rows = (await db.execute(q)).all()
        return [{
            'flock_id': r.flock_id, 'flock_code': r.flock_code, 'house_name': r.house_name,
            'bird_population': r.bird_population, 'total_eggs': int(r.total_eggs or 0),
            'damaged_eggs': int(r.damaged_eggs or 0), 'good_eggs': int(r.good_eggs or 0),
            'avg_laying_pct': r.avg_laying_pct,
        } for r in rows]

    @staticmethod
    async def production_by_house(db, date_from=None, date_to=None):
        q = (
            select(
                House.id.label('house_id'),
                House.name.label('house_name'),
                func.coalesce(func.sum(ProductionRecord.total_eggs), 0).label('total_eggs'),
                func.coalesce(func.sum(ProductionRecord.good_eggs), 0).label('good_eggs'),
                func.coalesce(func.sum(ProductionRecord.damaged_eggs), 0).label('damaged_eggs'),
                func.avg(ProductionRecord.laying_percentage).label('avg_laying_pct'),
            )
            .join(Flock, Flock.house_id == House.id)
            .join(ProductionRecord, ProductionRecord.flock_id == Flock.id)
        )
        if date_from: q = q.where(ProductionRecord.record_date >= date_from)
        if date_to: q = q.where(ProductionRecord.record_date <= date_to)
        q = q.group_by(House.id, House.name)
        rows = (await db.execute(q)).all()
        return [{'house_id': r.house_id, 'house_name': r.house_name, 'total_eggs': int(r.total_eggs or 0),
                 'good_eggs': int(r.good_eggs or 0), 'damaged_eggs': int(r.damaged_eggs or 0),
                 'avg_laying_pct': r.avg_laying_pct} for r in rows]

    @staticmethod
    async def feed_usage(db, params, flock_id=None, product_id=None, date_from=None, date_to=None):
        q = (
            select(FeedRecord, Flock.flock_code, House.name.label('house_name'), Product.name.label('product_name'))
            .join(Flock, FeedRecord.flock_id == Flock.id)
            .join(House, Flock.house_id == House.id)
            .outerjoin(Product, FeedRecord.product_id == Product.id)
        )
        if flock_id: q = q.where(FeedRecord.flock_id == flock_id)
        if product_id: q = q.where(FeedRecord.product_id == product_id)
        if date_from: q = q.where(FeedRecord.record_date >= date_from)
        if date_to: q = q.where(FeedRecord.record_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        tq = select(func.coalesce(func.sum(FeedRecord.quantity_used), 0), func.coalesce(func.sum(FeedRecord.total_cost), 0))
        if flock_id: tq = tq.where(FeedRecord.flock_id == flock_id)
        if date_from: tq = tq.where(FeedRecord.record_date >= date_from)
        if date_to: tq = tq.where(FeedRecord.record_date <= date_to)
        totals = (await db.execute(tq)).one()
        q = q.order_by(FeedRecord.record_date.desc()).offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        items = [{'id': r[0].id, 'record_date': r[0].record_date, 'flock_code': r[1], 'house_name': r[2],
                  'product_name': r[3], 'opening_quantity': r[0].opening_quantity, 'quantity_used': r[0].quantity_used,
                  'closing_quantity': r[0].closing_quantity, 'cost_per_unit': r[0].cost_per_unit, 'total_cost': r[0].total_cost}
                 for r in rows]
        return items, total, Decimal(totals[0] or 0), Decimal(totals[1] or 0)

    @staticmethod
    async def feed_by_flock(db, date_from=None, date_to=None):
        q = (
            select(
                Flock.id.label('flock_id'), Flock.flock_code,
                Product.name.label('product_name'),
                func.coalesce(func.sum(FeedRecord.quantity_used), 0).label('quantity_used'),
                func.coalesce(func.sum(FeedRecord.total_cost), 0).label('total_cost'),
            )
            .join(FeedRecord, FeedRecord.flock_id == Flock.id)
            .outerjoin(Product, FeedRecord.product_id == Product.id)
        )
        if date_from: q = q.where(FeedRecord.record_date >= date_from)
        if date_to: q = q.where(FeedRecord.record_date <= date_to)
        q = q.group_by(Flock.id, Flock.flock_code, Product.name)
        rows = (await db.execute(q)).all()
        return [{'flock_id': r.flock_id, 'flock_code': r.flock_code, 'product_name': r.product_name,
                 'quantity_used': Decimal(r.quantity_used or 0), 'total_cost': Decimal(r.total_cost or 0)} for r in rows]

    @staticmethod
    async def medication(db, params, flock_id=None, date_from=None, date_to=None):
        q = (
            select(MedicationRecord, Flock.flock_code, Product.name.label('product_name'))
            .join(Flock, MedicationRecord.flock_id == Flock.id)
            .outerjoin(Product, MedicationRecord.product_id == Product.id)
        )
        if flock_id: q = q.where(MedicationRecord.flock_id == flock_id)
        if date_from: q = q.where(MedicationRecord.record_date >= date_from)
        if date_to: q = q.where(MedicationRecord.record_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        tq = select(func.coalesce(func.sum(MedicationRecord.total_cost), 0))
        if flock_id: tq = tq.where(MedicationRecord.flock_id == flock_id)
        if date_from: tq = tq.where(MedicationRecord.record_date >= date_from)
        if date_to: tq = tq.where(MedicationRecord.record_date <= date_to)
        total_cost = Decimal((await db.execute(tq)).scalar() or 0)
        q = q.order_by(MedicationRecord.record_date.desc()).offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        items = [{'id': r[0].id, 'record_date': r[0].record_date, 'flock_code': r[1], 'product_name': r[2],
                  'disease_suspected': r[0].disease_suspected, 'quantity_used': r[0].quantity_used,
                  'cost_per_unit': r[0].cost_per_unit, 'total_cost': r[0].total_cost,
                  'withdrawal_period_days': r[0].withdrawal_period_days, 'recorded_by': r[0].recorded_by} for r in rows]
        return items, total, total_cost

    @staticmethod
    async def vaccination(db, params, flock_id=None, date_from=None, date_to=None):
        q = (
            select(VaccinationRecord, Flock.flock_code, Product.name.label('product_name'))
            .join(Flock, VaccinationRecord.flock_id == Flock.id)
            .outerjoin(Product, VaccinationRecord.product_id == Product.id)
        )
        if flock_id: q = q.where(VaccinationRecord.flock_id == flock_id)
        if date_from: q = q.where(VaccinationRecord.record_date >= date_from)
        if date_to: q = q.where(VaccinationRecord.record_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(VaccinationRecord.record_date.desc()).offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        items = [{'id': r[0].id, 'record_date': r[0].record_date, 'flock_code': r[1], 'product_name': r[2],
                  'disease_targeted': r[0].disease_targeted, 'administration_method': r[0].administration_method,
                  'quantity_used': r[0].quantity_used, 'total_cost': r[0].total_cost,
                  'next_due_date': r[0].next_due_date, 'recorded_by': r[0].recorded_by} for r in rows]
        return items, total

    @staticmethod
    async def upcoming_vaccinations(db, days_ahead: int = 30):
        from datetime import datetime as dt, timedelta
        today = dt.utcnow().date()
        cutoff = today + timedelta(days=days_ahead)
        q = (
            select(VaccinationRecord, Flock.flock_code, Product.name.label('product_name'))
            .join(Flock, VaccinationRecord.flock_id == Flock.id)
            .outerjoin(Product, VaccinationRecord.product_id == Product.id)
            .where(VaccinationRecord.next_due_date >= today)
            .where(VaccinationRecord.next_due_date <= cutoff)
        ).order_by(VaccinationRecord.next_due_date.asc())
        rows = (await db.execute(q)).all()
        return [{'id': r[0].id, 'flock_code': r[1], 'product_name': r[2],
                 'disease_targeted': r[0].disease_targeted, 'next_due_date': r[0].next_due_date,
                 'recorded_by': r[0].recorded_by} for r in rows]

    @staticmethod
    async def mortality_summary(db, date_from=None, date_to=None):
        q = select(
            func.coalesce(func.sum(MortalityRecord.quantity), 0),
            func.count(distinct(MortalityRecord.flock_id)),
        )
        if date_from: q = q.where(MortalityRecord.record_date >= date_from)
        if date_to: q = q.where(MortalityRecord.record_date <= date_to)
        r = (await db.execute(q)).one()
        return {'total_deaths': int(r[0] or 0), 'num_flocks_affected': int(r[1] or 0)}

    @staticmethod
    async def mortality_by_flock(db, date_from=None, date_to=None):
        q = (
            select(
                Flock.id.label('flock_id'),
                Flock.flock_code,
                Flock.initial_quantity,
                func.coalesce(func.sum(MortalityRecord.quantity), 0).label('total_deaths'),
            )
            .join(MortalityRecord, MortalityRecord.flock_id == Flock.id)
        )
        if date_from: q = q.where(MortalityRecord.record_date >= date_from)
        if date_to: q = q.where(MortalityRecord.record_date <= date_to)
        q = q.group_by(Flock.id, Flock.flock_code, Flock.initial_quantity)
        rows = (await db.execute(q)).all()
        result = []
        for r in rows:
            deaths = int(r.total_deaths or 0)
            initial = r.initial_quantity or 0
            remaining = initial - deaths
            rate = Decimal(deaths) / Decimal(initial) * 100 if initial > 0 else Decimal(0)
            result.append({'flock_id': r.flock_id, 'flock_code': r.flock_code, 'initial_population': initial,
                           'total_deaths': deaths, 'remaining_birds': remaining,
                           'mortality_rate': rate.quantize(Decimal('0.01'))})
        return result

    @staticmethod
    async def mortality_by_cause(db, date_from=None, date_to=None):
        q = (
            select(
                MortalityRecord.cause,
                func.count(MortalityRecord.id).label('num_records'),
                func.coalesce(func.sum(MortalityRecord.quantity), 0).label('total_deaths'),
            )
        )
        if date_from: q = q.where(MortalityRecord.record_date >= date_from)
        if date_to: q = q.where(MortalityRecord.record_date <= date_to)
        q = q.group_by(MortalityRecord.cause)
        rows = (await db.execute(q)).all()
        grand_total = sum(int(r.total_deaths or 0) for r in rows)
        return [{
            'cause': r.cause or 'Unknown',
            'num_records': r.num_records,
            'total_deaths': int(r.total_deaths or 0),
            'percentage': (Decimal(r.total_deaths or 0) / Decimal(grand_total) * 100).quantize(Decimal('0.01')) if grand_total > 0 else Decimal(0),
        } for r in rows]
