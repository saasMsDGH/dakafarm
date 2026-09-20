from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.api.v1.pos.models.sale import Sale, SaleItem
from app.api.v1.pos.models.customer import Customer
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.shared.pagination import PaginationParams


class SalesReportRepo:

    @staticmethod
    async def get_summary(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        customer_id: Optional[int] = None,
        payment_status: Optional[str] = None,
    ) -> dict:
        q = select(
            func.count(Sale.id).label('total_sales'),
            func.coalesce(func.sum(Sale.total_amount), 0).label('total_amount'),
            func.coalesce(func.sum(Sale.discount), 0).label('total_discount'),
            func.coalesce(func.sum(Sale.amount_paid), 0).label('amount_paid'),
            func.coalesce(func.sum(Sale.total_amount - Sale.amount_paid), 0).label('outstanding'),
        )
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        if customer_id:
            q = q.where(Sale.customer_id == customer_id)
        if payment_status:
            q = q.where(Sale.payment_status == payment_status)
        r = (await db.execute(q)).one()
        return {
            'total_sales': r.total_sales or 0,
            'total_amount': Decimal(r.total_amount or 0),
            'total_discount': Decimal(r.total_discount or 0),
            'amount_paid': Decimal(r.amount_paid or 0),
            'outstanding': Decimal(r.outstanding or 0),
        }

    @staticmethod
    async def list_detail(
        db: AsyncSession,
        params: PaginationParams,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        customer_id: Optional[int] = None,
        payment_status: Optional[str] = None,
    ):
        q = select(Sale).options(joinedload(Sale.customer))
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        if customer_id:
            q = q.where(Sale.customer_id == customer_id)
        if payment_status:
            q = q.where(Sale.payment_status == payment_status)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Sale.invoice_number.ilike(term))

        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        sort_col = getattr(Sale, params.sort_by, Sale.sale_date)
        q = q.order_by(sort_col.desc() if params.order == 'desc' else sort_col.asc())
        q = q.offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().unique().all())
        return items, total

    @staticmethod
    async def by_product(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        q = (
            select(
                Product.id.label('product_id'),
                Product.name.label('product_name'),
                ProductCategory.name.label('category'),
                func.coalesce(func.sum(SaleItem.quantity), 0).label('quantity_sold'),
                func.coalesce(func.sum(SaleItem.total_amount), 0).label('revenue'),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .outerjoin(ProductCategory, Product.category_id == ProductCategory.id)
        )
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        q = q.group_by(Product.id, Product.name, ProductCategory.name)
        rows = (await db.execute(q)).all()
        result = []
        for r in rows:
            qty = Decimal(r.quantity_sold or 0)
            rev = Decimal(r.revenue or 0)
            result.append({
                'product_id': r.product_id,
                'product_name': r.product_name,
                'category': r.category,
                'quantity_sold': qty,
                'revenue': rev,
                'avg_selling_price': rev / qty if qty > 0 else Decimal(0),
            })
        return result

    @staticmethod
    async def by_customer(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        q = (
            select(
                Customer.id.label('customer_id'),
                Customer.name.label('customer_name'),
                Customer.business_type,
                func.count(Sale.id).label('num_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_sales'),
                func.coalesce(func.sum(Sale.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Sale.total_amount - Sale.amount_paid), 0).label('outstanding'),
            )
            .join(Sale, Sale.customer_id == Customer.id)
        )
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        q = q.group_by(Customer.id, Customer.name, Customer.business_type)
        rows = (await db.execute(q)).all()
        return [{
            'customer_id': r.customer_id,
            'customer_name': r.customer_name,
            'business_type': r.business_type,
            'num_sales': r.num_sales,
            'total_sales': Decimal(r.total_sales or 0),
            'amount_paid': Decimal(r.amount_paid or 0),
            'outstanding': Decimal(r.outstanding or 0),
        } for r in rows]

    @staticmethod
    async def by_category(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        q = (
            select(
                ProductCategory.name.label('category'),
                func.coalesce(func.sum(SaleItem.quantity), 0).label('quantity'),
                func.coalesce(func.sum(SaleItem.total_amount), 0).label('revenue'),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(ProductCategory, Product.category_id == ProductCategory.id)
            .join(Product, Product.id == SaleItem.product_id)
        )
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        q = q.group_by(ProductCategory.name)
        rows = (await db.execute(q)).all()
        total_rev = sum(Decimal(r.revenue or 0) for r in rows)
        return [{
            'category': r.category,
            'quantity': Decimal(r.quantity or 0),
            'revenue': Decimal(r.revenue or 0),
            'percentage': (Decimal(r.revenue or 0) / total_rev * 100).quantize(Decimal('0.01')) if total_rev > 0 else Decimal(0),
        } for r in rows], total_rev

    @staticmethod
    async def payment_status_breakdown(
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        q = (
            select(
                Sale.payment_status,
                func.count(Sale.id).label('num_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_value'),
                func.coalesce(func.sum(Sale.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Sale.total_amount - Sale.amount_paid), 0).label('outstanding'),
            )
        )
        if date_from:
            q = q.where(Sale.sale_date >= date_from)
        if date_to:
            q = q.where(Sale.sale_date <= date_to)
        q = q.group_by(Sale.payment_status)
        rows = (await db.execute(q)).all()
        return [{
            'payment_status': r.payment_status,
            'num_sales': r.num_sales,
            'total_value': Decimal(r.total_value or 0),
            'amount_paid': Decimal(r.amount_paid or 0),
            'outstanding': Decimal(r.outstanding or 0),
        } for r in rows]
