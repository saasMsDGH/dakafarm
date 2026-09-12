import uuid
import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.pos.models.sale import Sale, SaleItem
from app.api.v1.pos.models.payment import Payment
from app.api.v1.pos.repository.SaleRepo import SaleRepo
from app.api.v1.pos.repository.PaymentRepo import PaymentRepo
from app.api.v1.pos.repository.CustomerRepo import CustomerRepo
from app.api.v1.inventory.service.StockMovementService import StockMovementService
from app.api.v1.inventory.schemas.StockMovementSchema import StockMovementCreate
from app.api.v1.pos.schemas.SaleSchema import SaleCreate, SaleListResponse
from app.api.v1.pos.schemas.PaymentSchema import PaymentCreate
from app.shared.pagination import PaginationParams, compute_pages

class SaleService:
    @staticmethod
    def _generate_invoice_number() -> str:
        ym = datetime.datetime.now().strftime("%Y%m")
        unique = uuid.uuid4().hex[:4].upper()
        return f"INV-{ym}-{unique}"

    @staticmethod
    def _generate_receipt_number() -> str:
        ym = datetime.datetime.now().strftime("%Y%m")
        unique = uuid.uuid4().hex[:4].upper()
        return f"RCPT-{ym}-{unique}"

    @staticmethod
    async def create(db: AsyncSession, request: SaleCreate, current_user_id: int) -> Sale:
        # 1. Validate Customer & Credit Limit
        customer = await CustomerRepo.get_by_id(db, request.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")

        # Calculate totals
        subtotal = sum((item.quantity * item.unit_price) for item in request.items)
        total_amount = subtotal - request.discount

        if request.amount_paid > total_amount:
            raise HTTPException(status_code=400, detail="Amount paid cannot exceed total amount.")

        if request.amount_paid > 0 and not request.payment_method:
            raise HTTPException(status_code=400, detail="Payment method is required if amount is paid.")

        new_debt = total_amount - request.amount_paid
        
        if new_debt > 0:
            current_outstanding = await SaleRepo.get_outstanding_balance(db, request.customer_id)
            projected_debt = Decimal(current_outstanding) + new_debt
            if projected_debt > customer.credit_limit:
                raise HTTPException(
                    status_code=400, 
                    detail=f"CREDIT LIMIT EXCEEDED: Sale would bring balance to {projected_debt:,.2f}. Limit is {customer.credit_limit:,.2f}."
                )

        # 2. Determine payment status
        if request.amount_paid == total_amount:
            payment_status = "PAID"
        elif request.amount_paid > 0:
            payment_status = "PARTIAL"
        else:
            payment_status = "UNPAID"

        # 3. Create Sale (flush)
        sale = Sale(
            invoice_number=SaleService._generate_invoice_number(),
            customer_id=request.customer_id,
            subtotal=subtotal,
            discount=request.discount,
            total_amount=total_amount,
            amount_paid=request.amount_paid,
            payment_status=payment_status,
            created_by=current_user_id
        )
        created_sale = await SaleRepo.create(db, sale)

        # 4. Process Items & Inventory
        for req_item in request.items:
            # Create Sale Item
            sale_item = SaleItem(
                sale_id=created_sale.id,
                product_id=req_item.product_id,
                quantity=req_item.quantity,
                unit_price=req_item.unit_price,
                total_amount=(req_item.quantity * req_item.unit_price)
            )
            await SaleRepo.create_item(db, sale_item)

            # Reduce Inventory (commit=False so it stays in transaction)
            movement_request = StockMovementCreate(
                product_id=req_item.product_id,
                movement_type="OUT",
                quantity=req_item.quantity,
                reference_type="Sale",
                reference_id=created_sale.id
            )
            # This will raise 400 if stock is insufficient
            await StockMovementService.create(db, movement_request, current_user_id, commit=False)

        # 5. Create Payment if money was received
        if request.amount_paid > 0:
            payment = Payment(
                sale_id=created_sale.id,
                receipt_number=SaleService._generate_receipt_number(),
                amount=request.amount_paid,
                payment_method=request.payment_method,
                received_by=current_user_id
            )
            await PaymentRepo.create(db, payment)

        # 6. Commit the entire transaction
        try:
            db.expunge(created_sale) # Detach so it doesn't cause expiration conflicts
            await db.commit()
            # Fetch freshly
            final_sale = await SaleRepo.get_by_id(db, created_sale.id)
            return final_sale
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")

    @staticmethod
    async def get_sale(db: AsyncSession, sale_id: int) -> Sale:
        sale = await SaleRepo.get_by_id(db, sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found.")
        return sale

    @staticmethod
    async def list_sales(db: AsyncSession, params: PaginationParams, customer_id: int = None) -> SaleListResponse:
        sales, total = await SaleRepo.list_sales(db, params, customer_id)
        return SaleListResponse(
            items=sales,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )

    @staticmethod
    async def add_payment(db: AsyncSession, sale_id: int, request: PaymentCreate, current_user_id: int) -> Payment:
        sale = await SaleRepo.get_by_id(db, sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found.")

        if sale.payment_status == "PAID":
            raise HTTPException(status_code=400, detail="Sale is already fully paid.")

        remaining = sale.total_amount - sale.amount_paid
        if request.amount > remaining:
            raise HTTPException(status_code=400, detail=f"Payment amount exceeds remaining balance of {remaining}.")

        # Create Payment
        payment = Payment(
            sale_id=sale.id,
            receipt_number=SaleService._generate_receipt_number(),
            amount=request.amount,
            payment_method=request.payment_method,
            received_by=current_user_id
        )
        created_payment = await PaymentRepo.create(db, payment)

        # Update Sale
        sale.amount_paid += request.amount
        if sale.amount_paid >= sale.total_amount:
            sale.payment_status = "PAID"
        else:
            sale.payment_status = "PARTIAL"

        try:
            db.expunge(created_payment)
            await db.commit()
            # Fetch freshly
            from sqlalchemy.future import select
            res = await db.execute(select(Payment).where(Payment.id == created_payment.id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed.")

    @staticmethod
    async def get_payments_for_sale(db: AsyncSession, sale_id: int) -> list[Payment]:
        return await PaymentRepo.list_payments_for_sale(db, sale_id)






