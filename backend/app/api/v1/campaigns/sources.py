"""Projections explicites de sources existantes ; jamais de lecture arbitraire de table."""
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from fastapi import HTTPException
from sqlalchemy import select
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.models.expense import Expense
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.feed_record import FeedRecord

from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.farm.models.medication_record import MedicationRecord
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.campaigns.poultry_models import PayrollAllocation

SOURCES = {
    'SALE': (Sale, 'sale_date', ('invoice_number','customer_id','subtotal','discount','total_amount')),
    'PURCHASE': (Purchase, 'purchase_date', ('purchase_number','supplier_id','subtotal','discount','total_amount')),
    'EXPENSE': (Expense, 'expense_date', ('expense_number','description','category','amount')),
    'CASH': (FinancialTransaction, 'transaction_date', ('account_id','transaction_type','direction','amount','reference_number')),
    'STOCK': (StockMovement, 'movement_date', ('product_id','movement_type','quantity','reference_type','reference_id','unit_cost_snapshot','cost_total_fcfa','valuation_basis')),
    'PRODUCTION': (ProductionRecord, 'record_date', ('flock_id','period_start_date','bird_days','total_birds','total_eggs','damaged_eggs','good_eggs')),
    'PAYROLL_ALLOC': (PayrollAllocation, 'allocation_date', ('payroll_id','campaign_id','employee_id','amount_fcfa','payroll_net_fcfa','pay_period','method')),
    'VACCINATION': (VaccinationRecord, 'record_date', ('flock_id','product_id','quantity_used','cost_per_unit','total_cost','disease_targeted')),
    'MEDICATION': (MedicationRecord, 'record_date', ('flock_id','product_id','quantity_used','cost_per_unit','total_cost','disease_suspected')),
    'MORTALITY': (MortalityRecord, 'record_date', ('flock_id','quantity','cause')),
    'FEED': (FeedRecord, 'record_date', ('flock_id','product_id','quantity_used','cost_per_unit','total_cost')),
}


def canonical(value):
    if isinstance(value, Decimal):
        return format(value.normalize(), 'f')
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode()).hexdigest()


def project(kind, row):
    _, date_field, fields = SOURCES[kind]
    when = getattr(row,date_field)
    if isinstance(when,datetime):when=when.astimezone(timezone.utc).date()
    raw = {field:canonical(getattr(row,field,None)) for field in fields}
    raw['date'] = canonical(when)
    title = raw.get('invoice_number') or raw.get('purchase_number') or raw.get('expense_number') or raw.get('reference_number') or f'{kind} #{row.id}'
    return {'type':kind,'id':row.id,'date':canonical(when),'label':str(title),'data':raw}


async def source_row(db, kind, source_id, lock=False):
    model = SOURCES[kind][0]
    q=select(model).where(model.id==source_id)
    if lock:q=q.with_for_update().execution_options(populate_existing=True)
    row=(await db.execute(q)).scalar_one_or_none()
    if row is None:raise HTTPException(404,'Source introuvable.')
    return row


def integer_amount(value):
    if value is None:raise HTTPException(422,'Montant absent : vérifier la source.')
    amount=Decimal(str(value))
    if not amount.is_finite() or amount!=amount.to_integral_value() or abs(amount)>9223372036854775807:
        raise HTTPException(422,'La source doit contenir un montant FCFA entier dans la plage autorisée ; aucune conversion implicite.')
    return int(amount)


def measures(snapshot):
    kind,raw=snapshot['type'],snapshot['data']
    if not snapshot.get('date'):
        raise HTTPException(422,'Date absente : corriger la source avant rattachement.')
    result={'revenue':0,'expense':0,'consumption':0,'cash_in':0,'cash_out':0,'funding_in':0,'funding_out':0,'unvalued':0,'unclassified':0,'eggs':0}
    if kind=='PAYROLL_ALLOC':result['expense']=integer_amount(raw['amount_fcfa'])
    elif kind=='SALE':result['revenue']=integer_amount(raw['total_amount'])
    elif kind=='EXPENSE':result['expense']=integer_amount(raw['amount'])
    elif kind=='CASH':
        amount=integer_amount(raw['amount'])
        if amount<=0 or raw['direction'] not in ['IN','OUT']:raise HTTPException(422,'Sens ou montant de trésorerie invalide.')
        result['cash_in' if raw['direction']=='IN' else 'cash_out']=amount
        if raw['transaction_type']=='OWNER_INVESTMENT':result['funding_in' if raw['direction']=='IN' else 'funding_out']=amount
        # Aucun double comptage avec les documents de vente, achat ou dépense.
        # Les autres flux demandent encore une qualification économique explicite.
        if raw['transaction_type'] not in {'SALE','PURCHASE','EXPENSE','PAYROLL','OWNER_INVESTMENT'}:
            result['unclassified']=1
    elif kind=='STOCK' and raw['movement_type']=='OUT':
        if raw.get('reference_type') not in {'Sale','FeedRecord','MedicationRecord','VaccinationRecord','MortalityRecord'}:
            # Une sortie manuelle n'est pas automatiquement une charge (ex. transfert).
            result['unvalued']=1
        elif raw.get('valuation_basis') not in {'DECLARED','WEIGHTED_AVERAGE','PRODUCTION_EXPENSED'} or raw.get('cost_total_fcfa') is None:
            result['unvalued']=1
        else:result['consumption']=integer_amount(raw['cost_total_fcfa'])
    elif kind=='STOCK' and raw['movement_type']=='ADJUSTMENT':result['unclassified']=1
    elif kind=='PRODUCTION':result['eggs']=int(raw['good_eggs'] or 0)
    if any(result[key]<0 for key in ['revenue','expense','consumption','eggs']):
        raise HTTPException(422,'Montant ou quantité négatif : corriger la source.')
    # Achats, alimentation et production ne sont pas ajoutés une seconde fois aux charges.
    return result
