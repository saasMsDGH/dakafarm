from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.shared.pagination import PaginationParams


class InventoryReportRepo:

    @staticmethod
    async def current_stock(db, params, category_id=None):
        q = select(Product, ProductCategory.name.label('cat_name')).outerjoin(
            ProductCategory, Product.category_id == ProductCategory.id
        ).where(Product.is_active == True)
        if category_id:
            q = q.where(Product.category_id == category_id)
        if params.search:
            q = q.where(Product.name.ilike(f'%{params.search}%'))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        result = []
        for row in rows:
            p = row[0]
            cat = row[1]
            stock = Decimal(p.current_stock or 0)
            reorder = Decimal(p.reorder_level or 0)
            if stock <= 0:
                status = 'OUT_OF_STOCK'
            elif stock <= reorder:
                status = 'LOW_STOCK'
            else:
                status = 'IN_STOCK'
            result.append({
                'product_id': p.id,
                'product_name': p.name,
                'category': cat,
                'unit_of_measure': p.unit_of_measure,
                'current_stock': stock,
                'reorder_level': reorder,
                'stock_status': status,
            })
        return result, total

    @staticmethod
    async def stock_movements(db, params, product_id=None, movement_type=None, date_from=None, date_to=None):
        q = select(StockMovement, Product.name.label('product_name'), ProductCategory.name.label('cat_name')).join(
            Product, StockMovement.product_id == Product.id
        ).outerjoin(ProductCategory, Product.category_id == ProductCategory.id)
        if product_id: q = q.where(StockMovement.product_id == product_id)
        if movement_type: q = q.where(StockMovement.movement_type == movement_type)
        if date_from: q = q.where(StockMovement.movement_date >= date_from)
        if date_to: q = q.where(StockMovement.movement_date <= date_to)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(StockMovement.movement_date.desc())
        q = q.offset(params.offset).limit(params.limit)
        rows = (await db.execute(q)).all()
        result = []
        for row in rows:
            sm = row[0]
            result.append({
                'id': sm.id,
                'movement_date': sm.movement_date,
                'product_name': row[1],
                'category': row[2],
                'movement_type': sm.movement_type,
                'quantity': Decimal(sm.quantity),
                'reference_type': sm.reference_type,
                'reference_id': sm.reference_id,
                'created_by': sm.created_by,
            })
        return result, total

    @staticmethod
    async def low_stock(db):
        q = select(Product, ProductCategory.name.label('cat_name')).outerjoin(
            ProductCategory, Product.category_id == ProductCategory.id
        ).where(Product.is_active == True).where(Product.current_stock <= Product.reorder_level)
        rows = (await db.execute(q)).all()
        return [{
            'product_id': row[0].id,
            'product_name': row[0].name,
            'category': row[1],
            'current_stock': Decimal(row[0].current_stock or 0),
            'reorder_level': Decimal(row[0].reorder_level or 0),
            'difference': Decimal(row[0].reorder_level or 0) - Decimal(row[0].current_stock or 0),
        } for row in rows]

    @staticmethod
    async def valuation(db):
        q = select(Product, ProductCategory.name.label('cat_name')).outerjoin(
            ProductCategory, Product.category_id == ProductCategory.id
        ).where(Product.is_active == True)
        rows = (await db.execute(q)).all()
        result = []
        total_val = Decimal(0)
        for row in rows:
            p = row[0]
            qty = Decimal(p.current_stock or 0)
            cost = Decimal(p.unit_price or 0)
            val = qty * cost
            total_val += val
            result.append({
                'product_id': p.id,
                'product_name': p.name,
                'category': row[1],
                'quantity': qty,
                'cost_per_unit': cost,
                'stock_value': val,
            })
        return result, total_val
