"""Extension fictive : quatre cycles de ponte et dix salaires réels dans le modèle RH."""
from calendar import monthrange
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from uuid import NAMESPACE_URL, uuid5
from sqlalchemy import select
from app.demo_seed import DATASET, AS_OF, stamp, month_after
from app.api.v1.campaigns.models import Activity, Campaign, CampaignEvent, DemoDataset, DemoSource, ProductValuation
from app.api.v1.campaigns.poultry_models import PoultryCampaign, PayrollAllocation, RetiredDemoSource
from app.api.v1.campaigns.sources import SOURCES, project, fingerprint, measures
from app.api.v1.campaigns.service import terminal_query
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.pos.models.purchase import Purchase, PurchaseItem
from app.api.v1.pos.models.purchase_payment import PurchasePayment
from app.api.v1.pos.models.sale import Sale, SaleItem
from app.api.v1.pos.models.payment import Payment
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.expense_payment import ExpensePayment
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.farm.models.house import House
from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.models.production_record import ProductionRecord
from app.api.v1.farm.models.vaccination_record import VaccinationRecord
from app.api.v1.farm.models.mortality_record import MortalityRecord
from app.api.v1.hr.models.employee import Employee
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.hr.models.payroll_payment import PayrollPayment

EXTENSION='dakrex-poultry-v2'
SALARY=100000


def allocate(total, weights):
    """Plus forts restes, entiers FCFA ; une paie n'est jamais multipliée par les bandes."""
    denominator=sum(weights.values())
    result={k:total*w//denominator for k,w in weights.items()}
    order=sorted(weights,key=lambda k:(-(total*weights[k]%denominator),k))
    for key in order[:total-sum(result.values())]:result[key]+=1
    return result


async def seed_poultry(db,actor,if_absent=False):
    from app.api.v1.campaigns.service import lock_key
    await lock_key(db,EXTENSION)
    old=await db.get(DemoDataset,EXTENSION)
    if old:return {**old.manifest,'replayed':True}
    baseline=await db.get(DemoDataset,DATASET)
    if baseline is None:raise RuntimeError('Importer le scénario multi-activité avant son extension avicole.')
    activity=await db.scalar(select(Activity).where(Activity.code=='DEMO-V1-ELEVAGE'))
    if activity is None:raise RuntimeError('Activité fictive élevage absente.')
    campaigns=list((await db.scalars(select(Campaign).where(Campaign.activity_id==activity.id).order_by(Campaign.start_date))).all())
    if len(campaigns)!=4:raise RuntimeError('Les campagnes ont changé : aucun remplacement implicite des essais utilisateur.')
    campaign_ids=[c.id for c in campaigns]

    async def save(row):
        db.add(row);await db.flush();await db.refresh(row);return row

    extension=await save(DemoDataset(id=EXTENSION,as_of=AS_OF,manifest={},created_by=actor))
    # L'ancien négoce reste consultable ; seules ses affectations fictives originales sont libérées.
    events=list((await db.scalars(terminal_query().where(CampaignEvent.campaign_id.in_(campaign_ids),CampaignEvent.action=='ASSIGN'))).all())
    old_products=set();old_accounts=set()
    for event in events:
        expected=str(uuid5(NAMESPACE_URL,f'{DATASET}:{event.source_type}:{event.source_id}'))
        if event.client_operation_id!=expected:raise RuntimeError('Affectation modifiée par l’utilisateur : remplacement avicole interrompu.')
        model=SOURCES[event.source_type][0];row=await db.get(model,event.source_id)
        if row is None or fingerprint(project(event.source_type,row))!=event.source_hash:
            raise RuntimeError('Source initiale modifiée : aucune réécriture de la démonstration.')
        if event.source_type=='STOCK':old_products.add(row.product_id)
        if event.source_type=='CASH':old_accounts.add(row.account_id)
        operation=str(uuid5(NAMESPACE_URL,f'{EXTENSION}:retire:{event.id}'))
        db.add(CampaignEvent(campaign_id=event.campaign_id,source_type=event.source_type,source_id=event.source_id,action='RELEASE',
            previous_event_id=event.id,client_operation_id=operation,payload_hash=fingerprint({'retired_by':EXTENSION,'event':str(event.id)}),
            source_hash=event.source_hash,snapshot=event.snapshot,reason='DÉMO V1 ARCHIVÉE : remplacée par un cycle de ponte détaillé, sans effacer les pièces.',actor_id=actor))
        db.add(RetiredDemoSource(source_type=event.source_type,source_id=event.source_id,extension_id=EXTENSION,reason='Ancien négoce de volailles fictif conservé en historique.'))
    await db.flush()
    for pid in old_products:
        product=await db.get(Product,pid);product.is_active=False
    for aid in old_accounts:
        account=await db.get(FinancialAccount,aid);account.is_active=False

    category=await save(ProductCategory(name='[DÉMO] Poules pondeuses et intrants',created_by=actor))
    category_id=category.id
    supplier=await save(Supplier(supplier_code='DEMO-AVIC-SUP',name='[DÉMO] Fournisseur avicole',created_by=actor));supplier_id=supplier.id
    customers=[await db.scalar(select(Customer).where(Customer.customer_code=='DEMO-V1-CUSTOMER'))]
    for i in range(2,11):
        customers.append(await save(Customer(customer_code=f'DEMO-AVIC-CLIENT-{i:02}',name=f'[DÉMO] Client œufs {i:02}',business_type='Revendeur fictif',created_by=actor)))
    customer_ids=[c.id for c in customers]
    employees=[]
    for i in range(1,11):
        e=await save(Employee(employee_code=f'DEMO-AVIC-EMP-{i:02}',first_name=f'Employé {i:02}',last_name='[DÉMO]',
            position='Équipe avicole fictive',employment_date=date(2024,1,1),status=True,created_by=actor));employees.append(e.id)
    account=await save(FinancialAccount(name='[DÉMO] Caisse poules pondeuses',account_type='CASH',opening_balance=0,created_by=actor));account_id=account.id
    source_counts=Counter();cohorts=[]

    async def attach(kind,row,campaign):
        snapshot=project(kind,row);when=date.fromisoformat(snapshot['date'])
        if not campaign.start_date<=when<=campaign.end_date or when>AS_OF:raise RuntimeError('Date de scénario avicole incohérente.')
        values=measures(snapshot)
        if values['unvalued'] or values['unclassified']:raise RuntimeError('Source avicole non qualifiée.')
        operation=str(uuid5(NAMESPACE_URL,f'{EXTENSION}:{kind}:{row.id}'))
        db.add(DemoSource(source_type=kind,source_id=row.id,dataset_id=DATASET))
        db.add(CampaignEvent(campaign_id=campaign.id,source_type=kind,source_id=row.id,action='ASSIGN',client_operation_id=operation,
            payload_hash=fingerprint({'extension':EXTENSION,'operation':operation}),source_hash=fingerprint(snapshot),
            snapshot={**snapshot,'currency':'XOF','demo_dataset':DATASET},reason='DÉMONSTRATION AVICOLE : hypothèses fictives en FCFA, sans protocole sanitaire.',actor_id=actor))
        await db.flush();source_counts[kind]+=1

    async def cash(campaign,when,amount,kind,reference):
        row=await save(FinancialTransaction(account_id=account_id,transaction_date=stamp(when),transaction_type=kind,direction='IN' if kind in ['SALE','OWNER_INVESTMENT'] else 'OUT',
            amount=Decimal(amount),reference_number=reference,description='[DÉMO] Cycle de ponte — flux fictif en FCFA',created_by=actor))
        await attach('CASH',row,campaign)

    async def stock(campaign,product,when,quantity,kind,ref_type,ref_id,basis=None):
        cost=Decimal(product.unit_price)
        if kind=='OUT' and product.current_stock<quantity:raise RuntimeError('Stock négatif dans le scénario avicole.')
        product.current_stock+=quantity if kind=='IN' else -quantity
        row=await save(StockMovement(product_id=product.id,movement_type=kind,quantity=quantity,movement_date=stamp(when),reference_type=ref_type,reference_id=ref_id,
            unit_cost_snapshot=cost if kind=='OUT' else None,valuation_basis=(basis or product.cost_basis) if kind=='OUT' else None,
            cost_total_fcfa=int((cost*quantity).quantize(Decimal('1'),rounding=ROUND_HALF_UP)) if kind=='OUT' else None,created_by=actor))
        await attach('STOCK',row,campaign)

    async def purchase(campaign,product,quantity,tag):
        amount=int(quantity*product.unit_price)
        row=await save(Purchase(purchase_number=tag,supplier_id=supplier_id,purchase_date=stamp(campaign.start_date),subtotal=amount,discount=0,total_amount=amount,amount_paid=amount,payment_status='PAID',created_by=actor))
        await save(PurchaseItem(purchase_id=row.id,product_id=product.id,quantity=quantity,unit_cost=product.unit_price,total_amount=amount))
        await attach('PURCHASE',row,campaign)
        await stock(campaign,product,campaign.start_date,quantity,'IN','Purchase',row.id)
        await save(ProductValuation(product_id=product.id,quantity=quantity,unit_cost=product.unit_price,basis='WEIGHTED_AVERAGE',origin='PURCHASE',purchase_id=row.id,reason='[DÉMO] Achat avicole en FCFA sur stock vide.',actor_id=actor))
        await save(PurchasePayment(purchase_id=row.id,payment_reference=tag+'P',amount=amount,payment_method='Cash',payment_date=stamp(campaign.start_date),paid_by=actor))
        await cash(campaign,campaign.start_date,amount,'PURCHASE',tag+'P')
        return amount

    async def sale(campaign,product,when,quantity,price,tag,client):
        amount=int(quantity*price)
        row=await save(Sale(invoice_number=tag,customer_id=client,sale_date=stamp(when),subtotal=amount,discount=0,total_amount=amount,amount_paid=amount,payment_status='PAID',created_by=actor))
        await save(SaleItem(sale_id=row.id,product_id=product.id,quantity=quantity,unit_price=price,total_amount=amount))
        await attach('SALE',row,campaign)
        await stock(campaign,product,when,quantity,'OUT','Sale',row.id,'PRODUCTION_EXPENSED' if product.unit_price==0 else None)
        await save(Payment(sale_id=row.id,receipt_number=tag+'P',amount=amount,payment_method='Cash',payment_date=stamp(when),received_by=actor))
        await cash(campaign,when,amount,'SALE',tag+'P')

    for index,campaign in enumerate(campaigns):
        tag=f'DEMO-PONTE-C{index+1}';initial=1000+200*index
        house=await save(House(name=f'[DÉMO] Poulailler {index+1}',capacity=initial,created_by=actor))
        flock=await save(Flock(flock_code=tag,house_id=house.id,breed='Pondeuses — hypothèse fictive',initial_quantity=initial,current_quantity=initial,arrival_date=campaign.start_date,status='Active',created_by=actor))
        products=[]
        for suffix,name,unit,cost in [('POULE','Poulettes prêtes à pondre','tête',3000),('OEUF','Œufs produits','œuf',0),('ALIM','Aliment pondeuses','kg',350),('VACC','Vaccin fictif','dose fictive',35)]:
            products.append(await save(Product(category_id=category_id,name=f'[DÉMO] C{index+1} · {name}',unit_of_measure=unit,unit_price=Decimal(cost),current_stock=Decimal(0),cost_basis='WEIGHTED_AVERAGE' if cost else 'DECLARED',created_by=actor)))
        birds,eggs,feed,vaccine=products
        assumptions={'initial_birds':initial,'bird_cost_fcfa':3000,'egg_price_fcfa':120,'end_hen_price_fcfa':1500,'feed_kg_per_bird_day':'0.110','feed_unit_fcfa':350,'vaccine_unit_fcfa':35,'employee_count':10,'monthly_salary_fcfa':SALARY,
            'salary_allocation':'Effectif initial des bandes actives ; plus forts restes, total mensuel conservé.', 'note':'Hypothèses de démonstration uniquement ; aucun prix de marché ni protocole sanitaire recommandé.'}
        await save(PoultryCampaign(campaign_id=campaign.id,flock_id=flock.id,bird_product_id=birds.id,egg_product_id=eggs.id,feed_product_id=feed.id,vaccine_product_id=vaccine.id,assumptions=assumptions))
        reserve=Decimal(initial)*Decimal((campaign.end_date-campaign.start_date).days+1)*Decimal('0.110')
        purchases=await purchase(campaign,birds,Decimal(initial),tag+'-POULES')
        purchases+=await purchase(campaign,feed,reserve,tag+'-ALIMENT')
        purchases+=await purchase(campaign,vaccine,Decimal(initial*8),tag+'-VACCIN')
        await save(ProductValuation(product_id=eggs.id,quantity=0,unit_cost=0,basis='DECLARED',origin='PRODUCTION',reason='[DÉMO] Charges de ponte reconnues via aliments, soins et salaires ; pas de double coût à la vente des œufs.',actor_id=actor))
        await cash(campaign,campaign.start_date,purchases+3000000,'OWNER_INVESTMENT',tag+'-CAPITAL')
        living=initial
        for month in range(24):
            start=month_after(campaign.start_date,month)
            if start>AS_OF:break
            end=min(date(start.year,start.month,monthrange(start.year,start.month)[1]),AS_OF)
            dead=max(1,initial//500) if end.day>=5 else 0
            mortality_date=start.replace(day=5)
            if dead:
                record=await save(MortalityRecord(flock_id=flock.id,record_date=mortality_date,quantity=dead,cause='[DÉMO] Hypothèse de mortalité, pas un diagnostic.',recorded_by=actor))
                await attach('MORTALITY',record,campaign)
                await stock(campaign,birds,mortality_date,Decimal(dead),'OUT','MortalityRecord',record.id)
            prior_living=living;living-=dead
            if month%3==0 and end.day>=8:
                when=start.replace(day=8)
                record=await save(VaccinationRecord(flock_id=flock.id,product_id=vaccine.id,record_date=when,quantity_used=Decimal(living),cost_per_unit=35,total_cost=living*35,
                    disease_targeted='[DÉMO] Vaccin fictif, scénario de coût',administration_method='Simulation uniquement',recorded_by=actor))
                await attach('VACCINATION',record,campaign)
                await stock(campaign,vaccine,when,Decimal(living),'OUT','VaccinationRecord',record.id)
            for part,(first,last) in enumerate([(1,min(15,end.day)),(16,end.day)]):
                if first>last:continue
                period_start=start.replace(day=first);when=start.replace(day=last)
                rate=55 if month==0 else 75 if month==1 else max(55,86-max(0,month-10)*2)
                bird_days=0;total_eggs=0
                for day in range(first,last+1):
                    count=prior_living if day<5 else living
                    bird_days+=count;total_eggs+=count*rate//100
                damaged=total_eggs*2//100;good=total_eggs-damaged
                record=await save(ProductionRecord(flock_id=flock.id,record_date=when,period_start_date=period_start,bird_days=bird_days,total_birds=living,total_eggs=total_eggs,damaged_eggs=damaged,good_eggs=good,
                    laying_percentage=(Decimal(total_eggs)*100/Decimal(bird_days)).quantize(Decimal('0.01')),recorded_by=actor))
                await attach('PRODUCTION',record,campaign)
                await stock(campaign,eggs,when,Decimal(good),'IN','ProductionRecord',record.id)
                quantity=Decimal(bird_days)*Decimal('0.110')
                opening=feed.current_stock
                record=await save(FeedRecord(flock_id=flock.id,product_id=feed.id,record_date=when,opening_quantity=opening,quantity_used=quantity,closing_quantity=opening-quantity,cost_per_unit=350,total_cost=quantity*350,recorded_by=actor))
                await attach('FEED',record,campaign)
                await stock(campaign,feed,when,quantity,'OUT','FeedRecord',record.id)
                await sale(campaign,eggs,when,Decimal(good),120,f'{tag}-{start:%Y%m}-{part}-OEUFS',customer_ids[(index+month*2+part)%10])
            when=end;amount=75000
            expense=await save(Expense(expense_number=f'{tag}-{start:%Y%m}-FRAIS',category='[DÉMO] Eau, énergie, litière, transport',description='Frais propres de la bande ; salaires exclus.',amount=amount,amount_paid=amount,payment_status='PAID',expense_date=stamp(when),paid_by=actor))
            await attach('EXPENSE',expense,campaign)
            ref=f'{tag}-{start:%Y%m}-FP'
            await save(ExpensePayment(expense_id=expense.id,account_id=account_id,payment_reference=ref,amount=amount,payment_method='Cash',payment_date=stamp(when),paid_by=actor))
            await cash(campaign,when,amount,'EXPENSE',ref)
            if month==23 and end==campaign.end_date:
                await sale(campaign,birds,end,Decimal(living),1500,tag+'-FIN-DE-CYCLE',customer_ids[index]);living=0
        flock.current_quantity=living;flock.status='Completed' if living==0 else 'Active'
        cohorts.append({'campaign':campaign,'initial':initial})
        await db.flush()

    # Une seule paie de 100 000 FCFA par employé/mois, ventilée entre les bandes actives.
    for month in range(34):
        first=month_after(date(2024,1,1),month)
        when=min(date(first.year,first.month,monthrange(first.year,first.month)[1]),AS_OF)
        active={c['campaign'].id:c['initial'] for c in cohorts if c['campaign'].start_date<=when<=c['campaign'].end_date}
        if not active:continue
        shares=allocate(SALARY,active)
        for emp_no,employee_id in enumerate(employees):
            payroll=await save(Payroll(employee_id=employee_id,pay_period=first.strftime('%Y-%m'),basic_salary=SALARY,allowances=0,deductions=0,net_salary=SALARY,amount_paid=SALARY,payment_date=when,payment_status='PAID',created_by=actor))
            for campaign_id,amount in shares.items():
                campaign=next(c for c in campaigns if c.id==campaign_id)
                allocation=await save(PayrollAllocation(payroll_id=payroll.id,campaign_id=campaign_id,employee_id=employee_id,allocation_date=when,amount_fcfa=amount,payroll_net_fcfa=SALARY,pay_period=payroll.pay_period,
                    method='Effectif initial des bandes actives, répartition entière par plus forts restes.',created_by=actor))
                await attach('PAYROLL_ALLOC',allocation,campaign)
                ref=f'PAIE-{payroll.id}-C{campaign_id}'
                await save(PayrollPayment(payroll_id=payroll.id,account_id=account_id,payment_reference=ref,amount=amount,payment_method='Cash',payment_date=stamp(when),paid_by=actor))
                await cash(campaign,when,amount,'PAYROLL',ref)
    manifest={'extension':EXTENSION,'campaign_ids':campaign_ids,'source_count':sum(source_counts.values()),'sources':dict(source_counts),'employee_ids':employees,'customer_ids':customer_ids,'employee_count':10,'monthly_salary_fcfa':SALARY,'monthly_payroll_fcfa':10*SALARY,'as_of':AS_OF.isoformat(),'retired_sources':len(events)}
    extension.manifest=manifest;await db.flush()
    return {**manifest,'replayed':False}
