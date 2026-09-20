from __future__ import annotations
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.assets.models.asset import Asset
from app.shared.pagination import PaginationParams


class AssetsReportRepo:

    @staticmethod
    async def register(db, params, status=None, condition=None):
        q = select(Asset)
        if status: q = q.where(Asset.status == status)
        if condition: q = q.where(Asset.condition == condition)
        if params.search: q = q.where(Asset.name.ilike(f'%{params.search}%') | Asset.asset_code.ilike(f'%{params.search}%'))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        tq = select(
            func.coalesce(func.sum(Asset.cost_price * Asset.quantity), 0),
            func.coalesce(func.sum(Asset.amount_paid), 0),
        )
        totals = (await db.execute(tq)).one()
        q = q.order_by(Asset.purchase_date.desc()).offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())
        return items, total, Decimal(totals[0] or 0), Decimal(totals[1] or 0)

    @staticmethod
    async def by_condition(db):
        q = (
            select(
                Asset.condition,
                func.count(Asset.id).label('num_assets'),
                func.coalesce(func.sum(Asset.cost_price * Asset.quantity), 0).label('total_cost'),
            )
        ).group_by(Asset.condition)
        rows = (await db.execute(q)).all()
        return [{'condition': r.condition or 'Unknown', 'num_assets': r.num_assets,
                 'total_cost': Decimal(r.total_cost or 0)} for r in rows]
