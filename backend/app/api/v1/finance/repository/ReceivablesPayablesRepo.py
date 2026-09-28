from typing import Tuple, List
from decimal import Decimal
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.supplier import Supplier
from app.shared.pagination import PaginationParams

class ReceivablesPayablesRepo:
    # ------------------ RECEIVABLES ------------------
    @staticmethod
    async def get_receivables_summary(db: AsyncSession, params: PaginationParams) -> Tuple[List[dict], int, Decimal]:
        balance_expr = func.sum(Sale.total_amount - Sale.amount_paid).label('outstanding_balance')
        
        base_query = (
            select(
                Customer.id.label('customer_id'),
                Customer.customer_code,
                Customer.name,
                Customer.phone,
                balance_expr
            )
            .join(Sale, Sale.customer_id == Customer.id)
            .where(Sale.payment_status.in_(['UNPAID', 'PARTIAL']))
            .group_by(Customer.id)
            .having(func.sum(Sale.total_amount - Sale.amount_paid) > 0)
        )

        if params.search:
            search_term = f"%{params.search}%"
            base_query = base_query.where(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.customer_code.ilike(search_term)
                )
            )

        total_outstanding_query = select(func.sum(base_query.subquery().c.outstanding_balance))
        res_tot_out = await db.execute(total_outstanding_query)
        total_outstanding = res_tot_out.scalar() or Decimal('0.00')

        count_query = select(func.count()).select_from(base_query.subquery())
        res_count = await db.execute(count_query)
        total_count = res_count.scalar() or 0

        paginated_query = base_query.order_by(Customer.name.asc()).offset(params.offset).limit(params.limit)
        res_data = await db.execute(paginated_query)
        items = [dict(row._mapping) for row in res_data.all()]

        return items, total_count, Decimal(total_outstanding)

    @staticmethod
    async def get_customer_receivables_detail(db: AsyncSession, customer_id: int) -> Tuple[Customer, List[dict], Decimal]:
        res_cust = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = res_cust.scalar_one_or_none()
        if not customer:
            return None, [], Decimal('0.00')

        sales_query = (
            select(
                Sale.id.label('sale_id'),
                Sale.invoice_number,
                Sale.sale_date,
                Sale.total_amount,
                Sale.amount_paid,
                (Sale.total_amount - Sale.amount_paid).label('balance_due')
            )
            .where(Sale.customer_id == customer_id)
            .where(Sale.payment_status.in_(['UNPAID', 'PARTIAL']))
            .where((Sale.total_amount - Sale.amount_paid) > 0)
            .order_by(Sale.sale_date.asc())
        )
        res_sales = await db.execute(sales_query)
        sales = [dict(row._mapping) for row in res_sales.all()]
        
        total_outstanding = sum(Decimal(s['balance_due']) for s in sales)
        return customer, sales, Decimal(total_outstanding)

    # ------------------ PAYABLES ------------------
    @staticmethod
    async def get_payables_summary(db: AsyncSession, params: PaginationParams) -> Tuple[List[dict], int, Decimal]:
        balance_expr = func.sum(Purchase.total_amount - Purchase.amount_paid).label('outstanding_balance')
        
        base_query = (
            select(
                Supplier.id.label('supplier_id'),
                Supplier.supplier_code,
                Supplier.name,
                Supplier.phone,
                balance_expr
            )
            .join(Purchase, Purchase.supplier_id == Supplier.id)
            .where(Purchase.payment_status.in_(['UNPAID', 'PARTIAL']))
            .group_by(Supplier.id)
            .having(func.sum(Purchase.total_amount - Purchase.amount_paid) > 0)
        )

        if params.search:
            search_term = f"%{params.search}%"
            base_query = base_query.where(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.supplier_code.ilike(search_term)
                )
            )

        total_outstanding_query = select(func.sum(base_query.subquery().c.outstanding_balance))
        res_tot_out = await db.execute(total_outstanding_query)
        total_outstanding = res_tot_out.scalar() or Decimal('0.00')

        count_query = select(func.count()).select_from(base_query.subquery())
        res_count = await db.execute(count_query)
        total_count = res_count.scalar() or 0

        paginated_query = base_query.order_by(Supplier.name.asc()).offset(params.offset).limit(params.limit)
        res_data = await db.execute(paginated_query)
        items = [dict(row._mapping) for row in res_data.all()]

        return items, total_count, Decimal(total_outstanding)

    @staticmethod
    async def get_supplier_payables_detail(db: AsyncSession, supplier_id: int) -> Tuple[Supplier, List[dict], Decimal]:
        res_sup = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
        supplier = res_sup.scalar_one_or_none()
        if not supplier:
            return None, [], Decimal('0.00')

        purchases_query = (
            select(
                Purchase.id.label('purchase_id'),
                Purchase.purchase_number,
                Purchase.purchase_date,
                Purchase.total_amount,
                Purchase.amount_paid,
                (Purchase.total_amount - Purchase.amount_paid).label('balance_due')
            )
            .where(Purchase.supplier_id == supplier_id)
            .where(Purchase.payment_status.in_(['UNPAID', 'PARTIAL']))
            .where((Purchase.total_amount - Purchase.amount_paid) > 0)
            .order_by(Purchase.purchase_date.asc())
        )
        res_purchases = await db.execute(purchases_query)
        purchases = [dict(row._mapping) for row in res_purchases.all()]
        
        total_outstanding = sum(Decimal(p['balance_due']) for p in purchases)
        return supplier, purchases, Decimal(total_outstanding)
