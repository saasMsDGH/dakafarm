from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.farm.models.flock import Flock
from app.api.v1.inventory.models.product import Product
from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.models.payroll import Payroll


class ManagementReportRepo:

    @staticmethod
    async def farm_summary(db, date_from: str, date_to: str):
        df = datetime.strptime(date_from, '%Y-%m-%d')
        dt = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

        async def scalar(q):
            return (await db.execute(q)).scalar() or 0

        fin_in = await scalar(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
            FinancialTransaction.direction == 'IN', FinancialTransaction.transaction_date >= df, FinancialTransaction.transaction_date <= dt))
        fin_out = await scalar(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
            FinancialTransaction.direction == 'OUT', FinancialTransaction.transaction_date >= df, FinancialTransaction.transaction_date <= dt))

        sales_q = select(func.coalesce(func.sum(Sale.total_amount), 0), func.coalesce(func.sum(Sale.amount_paid), 0)).where(
            Sale.sale_date >= df, Sale.sale_date <= dt)
        sales = (await db.execute(sales_q)).one()

        pur_q = select(func.coalesce(func.sum(Purchase.total_amount), 0), func.coalesce(func.sum(Purchase.amount_paid), 0)).where(
            Purchase.purchase_date >= df, Purchase.purchase_date <= dt)
        pur = (await db.execute(pur_q)).one()

        exp_q = select(func.coalesce(func.sum(Expense.amount), 0), func.coalesce(func.sum(Expense.amount_paid), 0)).where(
            Expense.expense_date >= df, Expense.expense_date <= dt)
        exp = (await db.execute(exp_q)).one()

        prod_q = select(
            func.coalesce(func.sum(ProductionRecord.total_eggs), 0),
            func.coalesce(func.sum(ProductionRecord.good_eggs), 0),
            func.coalesce(func.sum(ProductionRecord.damaged_eggs), 0),
            func.avg(ProductionRecord.laying_percentage),
        ).where(ProductionRecord.record_date >= df, ProductionRecord.record_date <= dt)
        prod = (await db.execute(prod_q)).one()

        active_flocks = await scalar(select(func.count(Flock.id)).where(Flock.status == True))
        total_birds = await scalar(select(func.coalesce(func.sum(Flock.current_quantity), 0)).where(Flock.status == True))
        mortality = await scalar(select(func.coalesce(func.sum(MortalityRecord.quantity), 0)).where(
            MortalityRecord.record_date >= df, MortalityRecord.record_date <= dt))

        total_products = await scalar(select(func.count(Product.id)).where(Product.is_active == True))
        low_stock = await scalar(select(func.count(Product.id)).where(
            Product.is_active == True, Product.current_stock <= Product.reorder_level, Product.current_stock > 0))
        out_stock = await scalar(select(func.count(Product.id)).where(
            Product.is_active == True, Product.current_stock <= 0))

        total_employees = await scalar(select(func.count(Employee.id)).where(Employee.status == True))
        pay_q = select(func.coalesce(func.sum(Payroll.amount_paid), 0), func.coalesce(func.sum(Payroll.net_salary - Payroll.amount_paid), 0)).where(
            Payroll.payment_date >= df, Payroll.payment_date <= dt)
        pay = (await db.execute(pay_q)).one()

        return {
            'period_from': date_from, 'period_to': date_to,
            'total_money_in': Decimal(fin_in), 'total_money_out': Decimal(fin_out),
            'net_movement': Decimal(fin_in) - Decimal(fin_out),
            'total_sales_amount': Decimal(sales[0]), 'sales_paid': Decimal(sales[1]),
            'sales_outstanding': Decimal(sales[0]) - Decimal(sales[1]),
            'total_purchases_amount': Decimal(pur[0]), 'purchases_paid': Decimal(pur[1]),
            'purchases_outstanding': Decimal(pur[0]) - Decimal(pur[1]),
            'total_expenses_amount': Decimal(exp[0]), 'expenses_paid': Decimal(exp[1]),
            'expenses_outstanding': Decimal(exp[0]) - Decimal(exp[1]),
            'total_eggs': int(prod[0] or 0), 'good_eggs': int(prod[1] or 0), 'damaged_eggs': int(prod[2] or 0),
            'avg_laying_pct': prod[3],
            'active_flocks': int(active_flocks), 'total_birds': int(total_birds), 'total_mortality': int(mortality),
            'total_products': int(total_products), 'low_stock_items': int(low_stock), 'out_of_stock_items': int(out_stock),
            'total_employees': int(total_employees), 'payroll_paid': Decimal(pay[0]), 'payroll_outstanding': Decimal(pay[1]),
        }

    @staticmethod
    async def yearly_report(db, year: int):
        months = []
        for month in range(1, 13):
            mf = datetime(year, month, 1)
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            mt = datetime(year, month, last_day, 23, 59, 59)
            label = f'{year}-{month:02d}'

            async def scalar(q):
                return Decimal((await db.execute(q)).scalar() or 0)

            sales = await scalar(select(func.coalesce(func.sum(Sale.total_amount), 0)).where(Sale.sale_date >= mf, Sale.sale_date <= mt))
            purchases = await scalar(select(func.coalesce(func.sum(Purchase.total_amount), 0)).where(Purchase.purchase_date >= mf, Purchase.purchase_date <= mt))
            expenses = await scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.expense_date >= mf, Expense.expense_date <= mt))
            money_in = await scalar(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
                FinancialTransaction.direction == 'IN', FinancialTransaction.transaction_date >= mf, FinancialTransaction.transaction_date <= mt))
            money_out = await scalar(select(func.coalesce(func.sum(FinancialTransaction.amount), 0)).where(
                FinancialTransaction.direction == 'OUT', FinancialTransaction.transaction_date >= mf, FinancialTransaction.transaction_date <= mt))
            eggs = int((await db.execute(select(func.coalesce(func.sum(ProductionRecord.total_eggs), 0)).where(
                ProductionRecord.record_date >= mf, ProductionRecord.record_date <= mt))).scalar() or 0)
            mort = int((await db.execute(select(func.coalesce(func.sum(MortalityRecord.quantity), 0)).where(
                MortalityRecord.record_date >= mf, MortalityRecord.record_date <= mt))).scalar() or 0)
            payroll = await scalar(select(func.coalesce(func.sum(Payroll.net_salary), 0)).where(
                Payroll.payment_date >= mf, Payroll.payment_date <= mt))

            months.append({'month': label, 'sales_amount': sales, 'purchases_amount': purchases,
                           'expenses_amount': expenses, 'money_in': money_in, 'money_out': money_out,
                           'egg_production': eggs, 'mortality': mort, 'payroll_net': payroll})
        return months

    @staticmethod
    async def customers_list(db, params):
        q = select(Customer)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Customer.name.ilike(term) | Customer.phone.ilike(term))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(Customer.name.asc()).offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())
        return items, total

    @staticmethod
    async def customers_sales(db, date_from=None, date_to=None):
        q = (
            select(
                Customer.id.label('customer_id'),
                Customer.name.label('customer_name'),
                func.count(Sale.id).label('num_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_sales'),
                func.coalesce(func.sum(Sale.amount_paid), 0).label('amount_paid'),
                func.coalesce(func.sum(Sale.total_amount - Sale.amount_paid), 0).label('outstanding'),
            )
            .join(Sale, Sale.customer_id == Customer.id)
        )
        if date_from: q = q.where(Sale.sale_date >= date_from)
        if date_to: q = q.where(Sale.sale_date <= date_to)
        q = q.group_by(Customer.id, Customer.name)
        rows = (await db.execute(q)).all()
        return [{'customer_id': r.customer_id, 'customer_name': r.customer_name, 'num_sales': r.num_sales,
                 'total_sales': Decimal(r.total_sales or 0), 'amount_paid': Decimal(r.amount_paid or 0),
                 'outstanding': Decimal(r.outstanding or 0)} for r in rows]

    @staticmethod
    async def customers_outstanding(db):
        q = (
            select(Customer.id, Customer.name, Sale.id.label('sale_id'), Sale.invoice_number,
                   Sale.sale_date, Sale.total_amount, Sale.amount_paid, Sale.payment_status)
            .join(Sale, Sale.customer_id == Customer.id)
            .where(Sale.payment_status.in_(['UNPAID', 'PARTIAL']))
        ).order_by(Sale.sale_date.desc())
        rows = (await db.execute(q)).all()
        return [{'customer_id': r[0], 'customer_name': r[1], 'sale_id': r[2], 'invoice_number': r[3],
                 'sale_date': str(r[4]), 'total_amount': Decimal(r[5] or 0), 'amount_paid': Decimal(r[6] or 0),
                 'outstanding': Decimal(r[5] or 0) - Decimal(r[6] or 0), 'payment_status': r[7]} for r in rows]

    @staticmethod
    async def suppliers_list(db, params):
        q = select(Supplier)
        if params.search:
            term = f'%{params.search}%'
            q = q.where(Supplier.name.ilike(term) | Supplier.phone.ilike(term))
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
        q = q.order_by(Supplier.name.asc()).offset(params.offset).limit(params.limit)
        items = list((await db.execute(q)).scalars().all())
        return items, total

    @staticmethod
    async def suppliers_purchases(db, date_from=None, date_to=None):
        q = (
            select(
                Supplier.id.label('supplier_id'), Supplier.name.label('supplier_name'),
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
    async def suppliers_outstanding(db):
        q = (
            select(Supplier.id, Supplier.name, Purchase.id.label('purchase_id'), Purchase.purchase_number,
                   Purchase.purchase_date, Purchase.total_amount, Purchase.amount_paid, Purchase.payment_status)
            .join(Purchase, Purchase.supplier_id == Supplier.id)
            .where(Purchase.payment_status.in_(['UNPAID', 'PARTIAL']))
        ).order_by(Purchase.purchase_date.desc())
        rows = (await db.execute(q)).all()
        return [{'supplier_id': r[0], 'supplier_name': r[1], 'purchase_id': r[2], 'purchase_number': r[3],
                 'purchase_date': str(r[4]), 'total_amount': Decimal(r[5] or 0), 'amount_paid': Decimal(r[6] or 0),
                 'outstanding': Decimal(r[5] or 0) - Decimal(r[6] or 0), 'payment_status': r[7]} for r in rows]
