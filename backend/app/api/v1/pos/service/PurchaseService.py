import uuid
import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.pos.models.purchase import Purchase, PurchaseItem
from app.api.v1.pos.models.purchase_payment import PurchasePayment
from app.api.v1.pos.repository.PurchaseRepo import PurchaseRepo
from app.api.v1.pos.repository.PurchasePaymentRepo import PurchasePaymentRepo
from app.api.v1.pos.repository.SupplierRepo import SupplierRepo
from app.api.v1.inventory.service.StockMovementService import StockMovementService
from app.api.v1.inventory.schemas.StockMovementSchema import StockMovementCreate
from app.api.v1.inventory.repository.ProductRepo import ProductRepo
from app.api.v1.pos.schemas.PurchaseSchema import PurchaseCreate, PurchaseListResponse
from app.api.v1.pos.schemas.PurchasePaymentSchema import PurchasePaymentCreate
from app.shared.pagination import PaginationParams, compute_pages


class PurchaseService:
    @staticmethod
    def _generate_purchase_number() -> str:
        ym = datetime.datetime.now().strftime("%Y%m")
        unique = uuid.uuid4().hex[:4].upper()
        return f"PO-{ym}-{unique}"

    @staticmethod
    def _generate_payment_reference() -> str:
        ym = datetime.datetime.now().strftime("%Y%m")
        unique = uuid.uuid4().hex[:4].upper()
        return f"PAY-{ym}-{unique}"

    @staticmethod
    async def create(db: AsyncSession, request: PurchaseCreate, current_user_id: int) -> Purchase:
        # 1. Validate Supplier
        supplier = await SupplierRepo.get_by_id(db, request.supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found.")

        # 2. Calculate totals
        subtotal = sum((item.quantity * item.unit_cost) for item in request.items)
        total_amount = subtotal - request.discount

        if request.amount_paid > total_amount:
            raise HTTPException(status_code=400, detail="Amount paid cannot exceed total amount.")

        if request.amount_paid > 0 and not request.payment_method:
            raise HTTPException(status_code=400, detail="Payment method is required if amount is paid.")

        # 3. Determine payment status
        if request.amount_paid == total_amount:
            payment_status = "PAID"
        elif request.amount_paid > 0:
            payment_status = "PARTIAL"
        else:
            payment_status = "UNPAID"

        # 4. Create Purchase (flush)
        purchase = Purchase(
            purchase_number=PurchaseService._generate_purchase_number(),
            supplier_id=request.supplier_id,
            subtotal=subtotal,
            discount=request.discount,
            total_amount=total_amount,
            amount_paid=request.amount_paid,
            payment_status=payment_status,
            notes=request.notes,
            created_by=current_user_id
        )
        created_purchase = await PurchaseRepo.create(db, purchase)

        # 5. Process Items & Inventory (stock IN)
        for req_item in request.items:
            # Validate product exists
            product = await ProductRepo.get_by_id(db, req_item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product with id {req_item.product_id} not found.")

            # Create Purchase Item
            purchase_item = PurchaseItem(
                purchase_id=created_purchase.id,
                product_id=req_item.product_id,
                quantity=req_item.quantity,
                unit_cost=req_item.unit_cost,
                total_amount=(req_item.quantity * req_item.unit_cost)
            )
            await PurchaseRepo.create_item(db, purchase_item)

            # Increase Inventory (movement_type="IN", commit=False)
            movement_request = StockMovementCreate(
                product_id=req_item.product_id,
                movement_type="IN",
                quantity=req_item.quantity,
                reference_type="Purchase",
                reference_id=created_purchase.id
            )
            await StockMovementService.create(db, movement_request, current_user_id, commit=False)

            # Update product's cost price (unit_price) with latest purchase cost
            product.unit_price = req_item.unit_cost
            if req_item.new_selling_price is not None:
                product.selling_price = req_item.new_selling_price

        # 6. Create Payment if money was paid to supplier
        if request.amount_paid > 0:
            payment = PurchasePayment(
                purchase_id=created_purchase.id,
                payment_reference=PurchaseService._generate_payment_reference(),
                amount=request.amount_paid,
                payment_method=request.payment_method,
                paid_by=current_user_id
            )
            await PurchasePaymentRepo.create(db, payment)

        # 7. Commit the entire transaction
        try:
            db.expunge(created_purchase)
            await db.commit()
            final_purchase = await PurchaseRepo.get_by_id(db, created_purchase.id)
            return final_purchase
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")

    @staticmethod
    async def get_purchase(db: AsyncSession, purchase_id: int) -> Purchase:
        purchase = await PurchaseRepo.get_by_id(db, purchase_id)
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found.")
        return purchase

    @staticmethod
    async def list_purchases(db: AsyncSession, params: PaginationParams, supplier_id: int = None) -> PurchaseListResponse:
        purchases, total = await PurchaseRepo.list_purchases(db, params, supplier_id)
        return PurchaseListResponse(
            items=purchases,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=compute_pages(total, params.limit)
        )

    @staticmethod
    async def add_payment(db: AsyncSession, purchase_id: int, request: PurchasePaymentCreate, current_user_id: int) -> PurchasePayment:
        purchase = await PurchaseRepo.get_by_id(db, purchase_id)
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found.")

        if purchase.payment_status == "PAID":
            raise HTTPException(status_code=400, detail="Purchase is already fully paid.")

        remaining = purchase.total_amount - purchase.amount_paid
        if request.amount > remaining:
            raise HTTPException(status_code=400, detail=f"Payment amount exceeds remaining balance of {remaining}.")

        # Create Payment
        payment = PurchasePayment(
            purchase_id=purchase.id,
            payment_reference=PurchaseService._generate_payment_reference(),
            amount=request.amount,
            payment_method=request.payment_method,
            paid_by=current_user_id
        )
        created_payment = await PurchasePaymentRepo.create(db, payment)

        # Update Purchase
        purchase.amount_paid += request.amount
        if purchase.amount_paid >= purchase.total_amount:
            purchase.payment_status = "PAID"
        else:
            purchase.payment_status = "PARTIAL"

        try:
            db.expunge(created_payment)
            await db.commit()
            res = await db.execute(select(PurchasePayment).where(PurchasePayment.id == created_payment.id))
            return res.scalar_one()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Transaction failed.")

    @staticmethod
    async def get_payments_for_purchase(db: AsyncSession, purchase_id: int) -> list[PurchasePayment]:
        return await PurchasePaymentRepo.list_payments_for_purchase(db, purchase_id)
