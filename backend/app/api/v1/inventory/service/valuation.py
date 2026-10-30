"""Coût moyen pondéré contrôlé, dans la transaction de l'achat."""
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from app.api.v1.campaigns.models import ProductValuation


def apply_purchase_cost(db,product,quantity,unit_cost,purchase_id,actor):
    quantity,unit_cost=Decimal(str(quantity)),Decimal(str(unit_cost))
    old=Decimal(str(product.current_stock or 0))
    if quantity<=0 or unit_cost<0:raise HTTPException(422,'Quantité ou coût d’achat invalide.')
    if old==0:
        new=unit_cost;basis='WEIGHTED_AVERAGE'
    elif old>0 and product.cost_basis in {'DECLARED','WEIGHTED_AVERAGE'}:
        new=((old*product.unit_price)+(quantity*unit_cost))/(old+quantity);basis='WEIGHTED_AVERAGE'
    else:
        # Préserver le comportement historique sans certifier un faux coût moyen.
        new=unit_cost;basis='UNVERIFIED'
    new=new.quantize(Decimal('0.000001'),rounding=ROUND_HALF_UP)
    product.unit_price=new;product.cost_basis=basis
    db.add(ProductValuation(product_id=product.id,quantity=old+quantity,unit_cost=new,basis=basis,
        origin='PURCHASE',purchase_id=purchase_id,reason='Achat, remise répartie au prorata des lignes.',actor_id=actor))
