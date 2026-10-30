"""Simulation DAKREX explicite et atomique. Jamais exécutée au démarrage de l'API."""
import argparse
import asyncio
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import os
from uuid import NAMESPACE_URL, uuid5
from sqlalchemy import func, select, text
import app.db
from app.core.database import engine, sessionlocal
from app.api.v1.user.models import Users, UserRole, Roles
from app.api.v1.campaigns.models import Activity, Campaign, CampaignEvent, DemoDataset, DemoSource, ProductValuation
from app.api.v1.campaigns.sources import fingerprint, measures, project
from app.api.v1.campaigns.service import _report
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.pos.models.purchase import Purchase, PurchaseItem
from app.api.v1.pos.models.purchase_payment import PurchasePayment
from app.api.v1.pos.models.sale import Sale, SaleItem
from app.api.v1.pos.models.payment import Payment
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.expense_payment import ExpensePayment
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction

DATASET = 'dakrex-coexistence-v1'
AS_OF = date(2026, 10, 30)
# code, nom, produit, coût, prix, volume mensuel, frais mensuels, délai encaissement, financement initial (%)
SCENARIOS = [
    ('ELEVAGE', 'Élevage', 'Volailles commercialisées', 1800, 2900, 100, 42000, 0, 100),
    ('BOUTIQUE', 'Boutique', 'Sacs de denrées', 3000, 4100, 150, 65000, 0, 100),
    ('BAR', 'Bar', 'Casiers de boissons', 4500, 4900, 80, 75000, 0, 100),
    ('GSM', 'GSM', 'Coupons et recharges', 800, 1000, 160, 18000, 0, 100),
    ('TELEPHONIE', 'Téléphonie', 'Téléphones et accessoires', 35000, 43000, 15, 50000, 1, 10),
    ('CULTURES', 'Cultures', 'Lots de récolte commercialisés', 7000, 11800, 60, 90000, 3, 40),
    ('PALME', 'Huile de palme', 'Bidons d’huile de palme', 9000, 14500, 65, 110000, 1, 100),
    ('PALMISTE', 'Palmiste', 'Lots de palmiste', 6000, 6600, 70, 65000, 2, 60),
]
STARTS = [date(2024, 1, 1), date(2024, 7, 1), date(2025, 7, 1), date(2026, 1, 1)]


def month_after(value, delta, day=1):
    number = value.year * 12 + value.month - 1 + delta
    return date(number // 12, number % 12 + 1, day)


def stamp(value):
    return datetime.combine(value, datetime.min.time(), timezone.utc)


async def seed_demo(db, actor, if_absent=False):
    """L'appelant valide une seule transaction ; tout échec laisse la base intacte."""
    await db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'), {'key': DATASET})
    old = await db.get(DemoDataset, DATASET)
    if old:
        if if_absent:
            # Le hook de déploiement ne doit pas réécrire les essais de l'utilisateur.
            return {**old.manifest, 'replayed': True}
        ids = old.manifest['campaign_ids']
        count = await db.scalar(select(func.count()).select_from(Campaign).where(Campaign.id.in_(ids)))
        events = await db.scalar(select(func.count()).select_from(CampaignEvent).where(CampaignEvent.campaign_id.in_(ids)))
        if count != 32 or events != old.manifest['source_count']:
            raise RuntimeError('Jeu de démonstration modifié : aucune réparation ni duplication implicite.')
        report = await _report(db, ids, AS_OF)
        if not report['quality']['result_available'] or report['totals'] != old.manifest['expected_totals']:
            raise RuntimeError('Données de démonstration modifiées : contrôler les sources avant une nouvelle importation.')
        return {**old.manifest, 'replayed': True}
    if await db.scalar(select(Activity.id).where(Activity.code.like('DEMO-V1-%')).limit(1)):
        raise RuntimeError('Codes de démonstration déjà utilisés sans manifeste : import refusé.')
    user = await db.get(Users, actor)
    admin = await db.scalar(select(UserRole.id).join(Roles, Roles.id == UserRole.role_id).where(UserRole.user_id == actor, Roles.name == 'admin'))
    if not user or not user.is_active or not admin:
        raise RuntimeError('Un administrateur actif doit être identifié pour signer la simulation.')

    async def save(row):
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    dataset = await save(DemoDataset(id=DATASET, as_of=AS_OF, manifest={}, created_by=actor))
    supplier = await save(Supplier(supplier_code='DEMO-V1-SUPPLIER', name='[DÉMO] Fournisseur fictif', created_by=actor))
    customer = await save(Customer(customer_code='DEMO-V1-CUSTOMER', name='[DÉMO] Client fictif', created_by=actor))
    supplier_id, customer_id = supplier.id, customer.id
    category = await save(ProductCategory(name='[DÉMO] Lots de simulation', created_by=actor))
    category_id = category.id
    campaign_ids, activity_ids, source_counts = [], [], Counter()
    expected = Counter(revenue=0, expense=0, consumption=0, cash_in=0, cash_out=0, funding_in=0, funding_out=0)

    async def attach(kind, row, campaign):
        snapshot = project(kind, row)
        when = date.fromisoformat(snapshot['date'])
        if not campaign.start_date <= when <= campaign.end_date or when > AS_OF:
            raise RuntimeError('Date incohérente dans la simulation.')
        values = measures(snapshot)
        if values['unvalued'] or values['unclassified']:
            raise RuntimeError('Source non valorisée dans la simulation.')
        for key in expected: expected[key] += values[key]
        operation = str(uuid5(NAMESPACE_URL, f'{DATASET}:{kind}:{row.id}'))
        db.add(DemoSource(source_type=kind,source_id=row.id,dataset_id=DATASET))
        db.add(CampaignEvent(campaign_id=campaign.id, source_type=kind, source_id=row.id, action='ASSIGN',
            client_operation_id=operation, payload_hash=fingerprint({'dataset': DATASET, 'operation': operation}),
            source_hash=fingerprint(snapshot), snapshot={**snapshot, 'currency': 'XOF','demo_dataset':DATASET},
            reason='DÉMONSTRATION : scénario synthétique en XOF, sans opération réelle.', actor_id=actor))
        await db.flush()
        source_counts[kind] += 1

    async def cash(account_id, campaign, when, amount, kind, direction, reference):
        if amount == 0: return
        row = await save(FinancialTransaction(account_id=account_id, transaction_date=stamp(when),
            transaction_type=kind, direction=direction, amount=Decimal(amount), reference_number=reference,
            description='[DÉMO] Flux synthétique — aucune transaction réelle', created_by=actor))
        await attach('CASH', row, campaign)

    for code, name, item_name, cost, price, volume, overhead, lag, funding_ratio in SCENARIOS:
        activity = await save(Activity(code='DEMO-V1-'+code, name=name, currency='XOF', demo_dataset=DATASET, created_by=actor))
        activity_ids.append(activity.id)
        account = await save(FinancialAccount(name='[DÉMO] Caisse '+name, account_type='CASH', opening_balance=0, created_by=actor))
        account_id = account.id
        for index, start in enumerate(STARTS):
            tag = f'DEMO-V1-{code}-C{index+1}'
            # La période inclut les encaissements différés après les dernières ventes.
            end = date.fromordinal(month_after(start, 24+lag).toordinal()-1)
            campaign = await save(Campaign(activity_id=activity.id, code=tag, name=f'{name} · campagne {index+1} ({start.year}–{end.year})',
                start_date=start, end_date=end, created_by=actor))
            campaign_ids.append(campaign.id)
            quantities = [volume * [100,110,95,120][index] * [80,100,120,90,110,100][m%6] // 10000 for m in range(24)]
            # Achat d'un lot complet : décaissement initial et consommation progressive.
            initial_quantity = sum(quantities) + volume
            total_cost = initial_quantity * cost
            monthly_expense = overhead * [100,110,95,120][index] // 100
            funding = (total_cost + monthly_expense*3) * funding_ratio // 100
            product = await save(Product(category_id=category_id, name=f'[DÉMO] {code} C{index+1} · {item_name}',
                unit_of_measure='lot', current_stock=Decimal(initial_quantity), unit_price=Decimal(cost),
                selling_price=Decimal(price), cost_basis='WEIGHTED_AVERAGE', created_by=actor))
            pid = product.id
            purchase = await save(Purchase(purchase_number=tag+'-ACH', supplier_id=supplier_id, purchase_date=stamp(start),
                subtotal=Decimal(total_cost), discount=0, total_amount=Decimal(total_cost), amount_paid=Decimal(total_cost), payment_status='PAID',
                notes='[DÉMO] Achat-revente simplifié ; ne modélise pas une transformation matière.', created_by=actor))
            purchase_id = purchase.id
            await save(PurchaseItem(purchase_id=purchase_id, product_id=pid, quantity=Decimal(initial_quantity), unit_cost=Decimal(cost), total_amount=Decimal(total_cost)))
            await attach('PURCHASE', purchase, campaign)
            movement = await save(StockMovement(product_id=pid, movement_type='IN', quantity=Decimal(initial_quantity),
                reference_type='Purchase', reference_id=purchase_id, movement_date=stamp(start), created_by=actor))
            await attach('STOCK', movement, campaign)
            await save(ProductValuation(product_id=pid, quantity=Decimal(initial_quantity), unit_cost=Decimal(cost), basis='WEIGHTED_AVERAGE',
                origin='PURCHASE', purchase_id=purchase_id, reason='[DÉMO] Premier lot acheté en XOF sur stock vide.', actor_id=actor))
            await save(PurchasePayment(purchase_id=purchase_id, payment_reference=tag+'-PA', amount=Decimal(total_cost), payment_method='Cash', payment_date=stamp(start), paid_by=actor))
            await cash(account_id, campaign, start, funding, 'OWNER_INVESTMENT', 'IN', tag+'-CAP')
            await cash(account_id, campaign, start, total_cost, 'PURCHASE', 'OUT', tag+'-PA')
            remaining = initial_quantity
            for m, quantity in enumerate(quantities):
                when = month_after(start, m, 15)
                if when > AS_OF: break
                suffix = f'{tag}-{when:%Y%m}'
                # Les prix varient légèrement ; BAR et PALMISTE ont des frais trop élevés.
                sale_price = price * [100,102,98,103,100,101][m%6] // 100
                amount = quantity * sale_price
                payment_date = month_after(start, m+lag, 22)
                paid = payment_date <= AS_OF
                sale = await save(Sale(invoice_number=suffix+'-V', customer_id=customer_id, sale_date=stamp(when),
                    subtotal=Decimal(amount), discount=0, total_amount=Decimal(amount), amount_paid=Decimal(amount if paid else 0),
                    payment_status='PAID' if paid else 'UNPAID', created_by=actor))
                sale_id = sale.id
                await save(SaleItem(sale_id=sale_id, product_id=pid, quantity=Decimal(quantity), unit_price=Decimal(sale_price), total_amount=Decimal(amount)))
                await attach('SALE', sale, campaign)
                consumed = quantity * cost
                remaining -= quantity
                movement = await save(StockMovement(product_id=pid, movement_type='OUT', quantity=Decimal(quantity), reference_type='Sale', reference_id=sale_id,
                    movement_date=stamp(when), unit_cost_snapshot=Decimal(cost), cost_total_fcfa=consumed, valuation_basis='WEIGHTED_AVERAGE', created_by=actor))
                await attach('STOCK', movement, campaign)
                if paid:
                    await save(Payment(sale_id=sale_id, receipt_number=suffix+'-PV', amount=Decimal(amount), payment_method='Cash', payment_date=stamp(payment_date), received_by=actor))
                    await cash(account_id, campaign, payment_date, amount, 'SALE', 'IN', suffix+'-PV')
                expense = await save(Expense(expense_number=suffix+'-F', category='[DÉMO] Frais de fonctionnement',
                    description='[DÉMO] Charges propres à cette campagne, sans ventilation commune implicite.', amount=Decimal(monthly_expense),
                    amount_paid=Decimal(monthly_expense), payment_status='PAID', expense_date=stamp(when), paid_by=actor))
                expense_id = expense.id
                await attach('EXPENSE', expense, campaign)
                await save(ExpensePayment(expense_id=expense_id, account_id=account_id, payment_reference=suffix+'-PF', amount=Decimal(monthly_expense),
                    payment_method='Cash', payment_date=stamp(when), paid_by=actor))
                await cash(account_id, campaign, when, monthly_expense, 'EXPENSE', 'OUT', suffix+'-PF')
            product.current_stock = Decimal(remaining)
            await db.flush()

    report = await _report(db, campaign_ids, AS_OF)
    if not report['quality']['result_available'] or len(report['by_activity']) != 8:
        raise RuntimeError('La simulation ne satisfait pas ses rapprochements : transaction annulée.')
    if any(report['totals'][key] != str(value) for key, value in expected.items()):
        raise RuntimeError('Les agrégats ne correspondent pas aux pièces de simulation.')
    manifest = {'dataset': DATASET, 'as_of': AS_OF.isoformat(), 'activity_ids': activity_ids, 'campaign_ids': campaign_ids,
        'activity_count': 8, 'campaigns_per_activity': 4, 'source_count': sum(source_counts.values()), 'sources': dict(source_counts),
        'expected_totals': report['totals'], 'scenarios': [{'activity': row['name'], 'status': row['status']} for row in report['by_activity']],
        'scope': 'Simulation financière de lots achetés/revendus ; GSM hors float, sans rendements biologiques ni transformation matière.'}
    dataset.manifest = manifest
    await db.flush()
    return {**manifest, 'replayed': False}


async def main(if_absent=False):
    if os.environ.get('DAKAFARM_DEMO_ALLOWED') != 'qualification-only':
        raise RuntimeError('Import désactivé : environnement de qualification explicite requis.')
    async with sessionlocal() as db:
        actor = await db.scalar(select(Users.id).join(UserRole, Users.id==UserRole.user_id).join(Roles, Roles.id==UserRole.role_id)
            .where(Roles.name=='admin', Users.is_active.is_(True)).order_by(Users.id).limit(1))
        if not actor: raise RuntimeError('Administrateur actif absent.')
        result = await seed_demo(db, actor, if_absent=if_absent)
        await db.commit()
        from app.poultry_seed import seed_poultry
        poultry=await seed_poultry(db,actor,if_absent=if_absent)
        await db.commit()
        print(json.dumps({k:poultry[k] for k in ['extension','employee_count','monthly_payroll_fcfa','source_count','replayed']},ensure_ascii=False))
        print(json.dumps({key: result[key] for key in ['dataset','activity_count','campaigns_per_activity','source_count','replayed']}, ensure_ascii=False))
    await engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importer la simulation financière de qualification, sans effacer les données existantes.')
    parser.add_argument('--confirm-qualification', required=True, action='store_true')
    parser.add_argument('--if-absent', action='store_true', help='Ne rien modifier si le jeu a déjà été importé (hook de déploiement).')
    args=parser.parse_args()
    try: asyncio.run(main(if_absent=args.if_absent))
    except Exception:
        # Les erreurs SQL peuvent contenir des paramètres privés ; ne pas les exposer.
        print('Import interrompu ; transaction annulée. Contrôler le diagnostic en environnement privé.')
        raise SystemExit(1)
