from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api.v1.pos.models.purchase import Purchase, PurchaseItem
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.shared.pagination import PaginationParams


class PurchasesReportRepo:

    @staticmethod
    async def get_summary(db, date_from=None, date_to=None, supplier_id=None, payment_status=None):
        q = select(
            func.count(Purchase.id).label('total_purchases'),
            func.coalesce(func.sum(Purchase.total_amount), 0).label('total_amount'),
            func.coalesce(func.sum(Purchase.amount_paid), 0).label('amount_paid'),
            func.coalesce(func.sum(Purchase.total_amount - Purchase.amount_paid), 0).label('outstanding'),
        )
        if date_from: q = q.where(Purchase.purchase_date >= date_from)
        if date_to: q = q.where(Purchase.purchase_date <= date_to)
        if supplier_id: q = q.where(Purchase.supplier_id == supplier_id)
        if payment_status: q = q.where(Purchase.payment_status == payment_status)
        r = (await db.execute(q)).one()
        return {
            'total_purchases': r.total_purchases or 0,
            'total_amount': Decimal(r.total_amount or 0),
            'amount_paid': Decimal(r.amount_paid or 0),
            'outstanding': Decimal(r.outstanding or 0),
        }

    @staticmethod
    async def list_detail(db, params, date_from=None, date_to=None, supplier_id=None, payment_status=None):
        q = select(Purchase).options(joinedload(Purchase.supplier))
        if date_from: q = q.where(Purchase.purchase_date >= date_from)
        if date_to: q = q.where(Purchase.purchase_date <= date_to)
        if supplier_id: q = q.where(Purchase.supplier_id == supplier_id)
        if payment_status: q = q.where(Purchase.payment_status == payment_status)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Purchase.purchase_number.ilike(term))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        sort_col = getattr(Purchase, params.sort_by, Purchase.purchase_date)
        q = q.order_by(sort_col.desc() if params.order == 'desc' else sort_col.asc())
        q = q.offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().unique().all())
        return items, total

    @staticmethod
    async def by_supplier(db, date_from=None, date_to=None):
        q = (
            select(
                Supplier.id.label('supplier_id'),
                Supplier.name.label('supplier_name'),
                func.count(Purchase.id).label('num_purchases'),
                func.coalesce(func.sum(Purchase.total_amount), 0).label('total_purchases'),
                func.coalesce(func.sum(Purchase.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Purchase.total_amount - Purchase.amount_paid), 0).label('outstanding'),
            )
            .join(Purchase, Purchase.supplier_id == Supplier.id)
        )
        if date_from: q = q.where(Purchase.purchase_date >= date_from)
        if date_to: q = q.where(Purchase.purchase_date <= date_to)
        q = q.group_by(Supplier.id, Supplier.name)
        rows = (await db.execute(q)).all()
        return [{'supplier_id': r.supplier_id, 'supplier_name': r.supplier_name, 'num_purchases': r.num_purchases,
                 'total_purchases': Decimal(r.total_purchases or 0), 'amount_paid': Decimal(r.amount_paid or 0),
                 'outstanding': Decimal(r.outstanding or 0)} for r in rows]

    @staticmethod
    async def by_product(db, date_from=None, date_to=None):
        q = (
            select(
                Product.id.label('product_id'),
                Product.name.label('product_name'),
                ProductCategory.name.label('category'),
                func.coalesce(func.sum(PurchaseItem.quantity), 0).label('quantity_purchased'),
                func.coalesce(func.sum(PurchaseItem.total_amount), 0).label('total_cost'),
            )
            .join(PurchaseItem, PurchaseItem.product_id == Product.id)
            .join(Purchase, PurchaseItem.purchase_id == Purchase.id)
            .outerjoin(ProductCategory, Product.category_id == ProductCategory.id)
        )
        if date_from: q = q.where(Purchase.purchase_date >= date_from)
        if date_to: q = q.where(Purchase.purchase_date <= date_to)
        q = q.group_by(Product.id, Product.name, ProductCategory.name)
        rows = (await db.execute(q)).all()
        result = []
        for r in rows:
            qty = Decimal(r.quantity_purchased or 0)
            cost = Decimal(r.total_cost or 0)
            result.append({'product_id': r.product_id, 'product_name': r.product_name, 'category': r.category,
                           'quantity_purchased': qty, 'total_cost': cost,
                           'avg_unit_cost': cost / qty if qty > 0 else Decimal(0)})
        return result
