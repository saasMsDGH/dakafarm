from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import exists, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.campaigns.models import Activity, Campaign, CampaignEvent, ProductValuation, DemoSource
from app.api.v1.campaigns.sources import SOURCES, fingerprint, measures, project, source_row
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.pos.models.payment import Payment
from app.api.v1.pos.models.purchase_payment import PurchasePayment
from app.api.v1.pos.models.expense_payment import ExpensePayment


def terminal_query():
    child=aliased(CampaignEvent)
    return select(CampaignEvent).where(~exists(select(child.id).where(child.previous_event_id==CampaignEvent.id)))


def event_json(e):
    return {'id':str(e.id),'campaign_id':e.campaign_id,'source_type':e.source_type,'source_id':e.source_id,
            'action':e.action,'previous_event_id':str(e.previous_event_id) if e.previous_event_id else None,
            'reason':e.reason,'actor_id':e.actor_id,'created_at':e.created_at.isoformat(),
            'source_hash':e.source_hash,'snapshot':e.snapshot}


async def lock_key(db,key):
    await db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'),{'key':key})


async def create_activity(db,request,actor):
    row=Activity(**request.model_dump(),created_by=actor)
    db.add(row)
    try:await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'Code activité déjà utilisé.') from None
    await db.refresh(row)
    return activity_json(row)


def activity_json(row):return {'id':row.id,'code':row.code,'name':row.name,'currency':row.currency,'is_active':row.is_active,'demo_dataset':row.demo_dataset}
def campaign_json(row):return {'id':row.id,'activity_id':row.activity_id,'code':row.code,'name':row.name,'start_date':row.start_date.isoformat(),'end_date':row.end_date.isoformat() if row.end_date else None,'status':row.status}


async def create_campaign(db,request,actor):
    activity=await db.get(Activity,request.activity_id)
    if activity is None or not activity.is_active:raise HTTPException(422,'Activité absente ou désactivée.')
    row=Campaign(**request.model_dump(),created_by=actor);db.add(row)
    try:await db.commit()
    except IntegrityError:
        await db.rollback();raise HTTPException(409,'Code campagne déjà utilisé.') from None
    await db.refresh(row)
    return campaign_json(row)


async def replay(db,operation_id,payload_hash):
    await lock_key(db,'campaign-command:'+str(operation_id))
    old=await db.scalar(select(CampaignEvent).where(CampaignEvent.client_operation_id==str(operation_id)))
    if old:
        if old.payload_hash!=payload_hash:raise HTTPException(409,'Identifiant de commande réutilisé avec un autre contenu.')
        return event_json(old)


async def assign(db,campaign_id,request,actor):
    payload={'action':'ASSIGN','campaign_id':campaign_id,**request.model_dump(mode='json'),'actor_id':actor}
    h=fingerprint(payload)
    try:
        previous=await replay(db,request.client_operation_id,h)
        if previous:return previous
        await lock_key(db,f'{request.source_type}:{request.source_id}')
        latest=await db.scalar(terminal_query().where(CampaignEvent.source_type==request.source_type,CampaignEvent.source_id==request.source_id))
        if latest and latest.action=='ASSIGN':raise HTTPException(409,'Source déjà rattachée. Corriger explicitement son affectation avant de la déplacer.')
        campaign=await db.scalar(select(Campaign).where(Campaign.id==campaign_id).with_for_update())
        if campaign is None:raise HTTPException(404,'Campagne introuvable.')
        activity=await db.get(Activity,campaign.activity_id)
        if campaign.status!='OPEN' or not activity.is_active:raise HTTPException(409,'Campagne fermée ou activité désactivée.')
        demo=await db.get(DemoSource,(request.source_type,request.source_id))
        if (demo.dataset_id if demo else None)!=activity.demo_dataset:
            raise HTTPException(409,'Une source de démonstration doit rester dans son jeu fictif ; les sources réelles doivent rester dans les activités réelles.')
        row=await source_row(db,request.source_type,request.source_id,lock=True)
        snapshot=project(request.source_type,row)
        if fingerprint(snapshot)!=request.source_hash:raise HTTPException(409,'La source a changé depuis sa consultation. Rechargez-la avant validation.')
        measures(snapshot)  # Refuser les montants non entiers, absents ou mal signés.
        when=date.fromisoformat(snapshot['date'])
        if when<campaign.start_date or (campaign.end_date and when>campaign.end_date):
            raise HTTPException(422,'La date de la source est hors de la période de campagne.')
        snapshot={**snapshot,'currency':request.confirm_currency,'demo_dataset':activity.demo_dataset}
        event=CampaignEvent(campaign_id=campaign_id,source_type=request.source_type,source_id=request.source_id,
            action='ASSIGN',previous_event_id=latest.id if latest else None,client_operation_id=str(request.client_operation_id),
            payload_hash=h,source_hash=request.source_hash,snapshot=snapshot,reason=request.reason,actor_id=actor)
        db.add(event);await db.commit();await db.refresh(event)
        return event_json(event)
    except Exception:
        await db.rollback();raise


async def release(db,event_id,request,actor):
    h=fingerprint({'action':'RELEASE','event_id':str(event_id),**request.model_dump(mode='json'),'actor_id':actor})
    try:
        previous=await replay(db,request.client_operation_id,h)
        if previous:return previous
        old=await db.get(CampaignEvent,event_id)
        if old is None:raise HTTPException(404,'Affectation introuvable.')
        await lock_key(db,f'{old.source_type}:{old.source_id}')
        latest=await db.scalar(terminal_query().where(CampaignEvent.source_type==old.source_type,CampaignEvent.source_id==old.source_id))
        if latest.id!=old.id or old.action!='ASSIGN':raise HTTPException(409,'Cette affectation a déjà été corrigée.')
        campaign=await db.scalar(select(Campaign).where(Campaign.id==old.campaign_id).with_for_update())
        if campaign.status!='OPEN':raise HTTPException(409,'Une campagne fermée ne peut pas être modifiée.')
        event=CampaignEvent(campaign_id=old.campaign_id,source_type=old.source_type,source_id=old.source_id,
            action='RELEASE',previous_event_id=old.id,client_operation_id=str(request.client_operation_id),payload_hash=h,
            source_hash=old.source_hash,snapshot=old.snapshot,reason=request.reason,actor_id=actor)
        db.add(event);await db.commit();await db.refresh(event)
        return event_json(event)
    except Exception:
        await db.rollback();raise


async def list_sources(db,kind,limit,before_id):
    model=SOURCES[kind][0]
    query=select(model).order_by(model.id.desc()).limit(limit+1)
    if before_id:query=query.where(model.id<before_id)
    rows=list((await db.scalars(query)).all());page=rows[:limit]
    active=list((await db.scalars(terminal_query().where(CampaignEvent.source_type==kind,CampaignEvent.source_id.in_([r.id for r in page]),CampaignEvent.action=='ASSIGN'))).all())
    assigned={e.source_id:e for e in active}
    items=[]
    for row in page:
        snapshot=project(kind,row);e=assigned.get(row.id)
        try:metrics=measures(snapshot);issue=None
        except HTTPException as error:metrics=None;issue=error.detail
        items.append({'source':snapshot,'source_hash':fingerprint(snapshot),'measures':metrics,'issue':issue,
            'assignment':{'event_id':str(e.id),'campaign_id':e.campaign_id,'source_changed':e.source_hash!=fingerprint(snapshot)} if e else None,
            'currency_confirmed':e.snapshot.get('currency') if e else None})
    return {'items':items,'next_cursor':page[-1].id if len(rows)>limit else None}


async def quality(db):
    active=list((await db.scalars(terminal_query().where(CampaignEvent.action=='ASSIGN'))).all())
    by_kind=defaultdict(set)
    for e in active:by_kind[e.source_type].add(e.source_id)
    counts={}
    for kind,(model,_,_) in SOURCES.items():
        total=await db.scalar(select(func.count()).select_from(model))
        # Une affectation d'une source supprimée ne doit pas masquer une autre source non affectée.
        present=await db.scalar(select(func.count()).select_from(model).where(model.id.in_(by_kind[kind])))
        counts[kind]={'total':total,'assigned':present,'unassigned':total-present}
    return {'sources':counts,'unassigned_total':sum(x['unassigned'] for x in counts.values()),
            'historical_currency':'Non présumée ; confirmation XOF requise à chaque rattachement.'}


async def report(db,campaign_ids,as_of):
    # Les différentes requêtes du rapport doivent lire le même état PostgreSQL.
    # Session indépendante : aucune écriture en attente de l'appelant n'est validée.
    async with AsyncSession(bind=db.bind) as snapshot_db:
        await snapshot_db.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        return await _report(snapshot_db,campaign_ids,as_of)


async def _report(db,campaign_ids,as_of):
    ids=sorted(set(campaign_ids))
    campaigns=list((await db.scalars(select(Campaign).where(Campaign.id.in_(ids)))).all())
    if len(campaigns)!=len(ids):raise HTTPException(404,'Une campagne est introuvable.')
    activity_ids={c.activity_id for c in campaigns}
    activities=list((await db.scalars(select(Activity).where(Activity.id.in_(activity_ids)))).all())
    datasets={a.demo_dataset for a in activities}
    if len(datasets)>1:
        raise HTTPException(422,'Séparer les données de démonstration des données réelles avant consolidation.')
    if any(a.currency!='XOF' for a in activities):raise HTTPException(422,'Les devises ne peuvent pas être mélangées.')
    events=list((await db.scalars(terminal_query().where(CampaignEvent.action=='ASSIGN',CampaignEvent.campaign_id.in_(ids)).order_by(CampaignEvent.id).limit(10001))).all())
    if len(events)>10000:raise HTTPException(413,'Plus de 10 000 sources : réduire la sélection pour valider les données.')
    # Charger les sources en lots, sans requête par événement et sans accès aux secrets utilisateurs.
    current={}
    for kind,(model,_,_) in SOURCES.items():
        wanted=[e.source_id for e in events if e.source_type==kind]
        if wanted:
            for row in (await db.scalars(select(model).where(model.id.in_(wanted)))).all():current[(kind,row.id)]=project(kind,row)
    keys=['revenue','expense','consumption','cash_in','cash_out','funding_in','funding_out','unvalued','unclassified','eggs']
    def empty():return {k:0 for k in keys}
    totals=empty();months=defaultdict(empty);years=defaultdict(empty);per_campaign={c.id:empty() for c in campaigns}
    per_activity={a.id:empty() for a in activities}
    activity_dates={a.id:defaultdict(empty) for a in activities}
    campaign_activity={c.id:c.activity_id for c in campaigns}
    activity_dataset={a.id:a.demo_dataset for a in activities}
    issues=[];sources=[]
    for e in events:
        snapshot=e.snapshot
        when=date.fromisoformat(snapshot['date']) if snapshot.get('date') else None
        if when and when>as_of:continue
        live=current.get((e.source_type,e.source_id))
        drift=live is None or fingerprint(live)!=e.source_hash
        if drift:issues.append({'event_id':str(e.id),'type':'SOURCE_CHANGED' if live else 'SOURCE_MISSING','source_type':e.source_type,'source_id':e.source_id})
        values=measures(snapshot)
        if values['unvalued']:issues.append({'event_id':str(e.id),'type':'UNVALUED_CONSUMPTION','source_type':e.source_type,'source_id':e.source_id})
        if values['unclassified']:issues.append({'event_id':str(e.id),'type':'ECONOMIC_CLASSIFICATION_REQUIRED','source_type':e.source_type,'source_id':e.source_id})
        aid=campaign_activity[e.campaign_id]
        if snapshot.get('demo_dataset')!=activity_dataset[aid]:
            issues.append({'event_id':str(e.id),'type':'SOURCE_PROVENANCE_MISMATCH','source_type':e.source_type,'source_id':e.source_id})
        for dest in [totals,months[when.strftime('%Y-%m')] if when else months['Sans date'],years[str(when.year)] if when else years['Sans date'],per_campaign[e.campaign_id],per_activity[aid],activity_dates[aid][when.isoformat()]]:
            for key in keys:dest[key]+=values[key]
        sources.append({**event_json(e),'source_changed':drift})
    # Une vente ou un relevé d'alimentation ne peut afficher une marge à coût nul
    # simplement parce que ses mouvements de stock n'ont pas été rattachés.
    included={(e['source_type'],e['source_id']):e for e in sources}
    payment_models={'SALE':(Payment,'receipt_number','sale_id','IN'),
                    'PURCHASE':(PurchasePayment,'payment_reference','purchase_id','OUT'),
                    'EXPENSE':(ExpensePayment,'payment_reference','expense_id','OUT')}
    for kind,(model,ref_field,parent_field,direction) in payment_models.items():
        cash_events=[e for e in sources if e['source_type']=='CASH' and e['snapshot']['data']['transaction_type']==kind]
        refs=[e['snapshot']['data'].get('reference_number') for e in cash_events]
        payments={getattr(p,ref_field):p for p in (await db.scalars(select(model).where(getattr(model,ref_field).in_([r for r in refs if r])))).all()} if refs else {}
        for event in cash_events:
            raw=event['snapshot']['data'];payment=payments.get(raw.get('reference_number'))
            valid=payment is not None and Decimal(raw['amount'])==payment.amount and raw['direction']==direction
            if valid and kind=='EXPENSE':valid=raw['account_id']==payment.account_id
            parent=included.get((kind,getattr(payment,parent_field))) if valid else None
            if not parent or parent['campaign_id']!=event['campaign_id']:
                issues.append({'event_id':event['id'],'type':'CASH_DOCUMENT_LINK_REQUIRED','source_type':'CASH','source_id':event['source_id']})
    for event in sources:
        if event['source_type']!='STOCK':continue
        raw=event['snapshot']['data']
        parent_kind={'Sale':'SALE','FeedRecord':'FEED'}.get(raw.get('reference_type'))
        if parent_kind:
            parent=included.get((parent_kind,raw.get('reference_id')))
            if not parent or parent['campaign_id']!=event['campaign_id']:
                issues.append({'event_id':event['id'],'type':'DOCUMENT_ASSIGNMENT_REQUIRED','source_type':parent_kind,'source_id':raw.get('reference_id')})
    for kind,reference in [('SALE','Sale'),('FEED','FeedRecord')]:
        wanted=[e['source_id'] for e in sources if e['source_type']==kind]
        if not wanted:continue
        movements=list((await db.scalars(select(StockMovement).where(StockMovement.reference_type==reference,StockMovement.reference_id.in_(wanted)))).all())
        for sid in wanted:
            origin=included[(kind,sid)]
            linked=[m for m in movements if m.reference_id==sid]
            if not linked:
                issues.append({'event_id':origin['id'],'type':'STOCK_LINK_MISSING','source_type':kind,'source_id':sid})
            for movement in linked:
                target=included.get(('STOCK',movement.id))
                if not target or target['campaign_id']!=origin['campaign_id']:
                    issues.append({'event_id':origin['id'],'type':'STOCK_ASSIGNMENT_REQUIRED','source_type':'STOCK','source_id':movement.id})
    ready=not issues
    cash_ready=not any(i['source_type']=='CASH' and i['type'] in {'SOURCE_CHANGED','SOURCE_MISSING'} for i in issues)
    def serialize(v):
        return {**{k:str(v[k]) for k in keys if k not in ['unvalued','unclassified','eggs']},'unvalued':v['unvalued'],'unclassified':v['unclassified'],'eggs':str(v['eggs']),
            'known_result_fcfa':str(v['revenue']-v['expense']-v['consumption']),
            'result_fcfa':str(v['revenue']-v['expense']-v['consumption']) if ready else None,
            'cash_before_funding_fcfa':str(v['cash_in']-v['cash_out']-v['funding_in']+v['funding_out']) if cash_ready else None,
            'cash_net_fcfa':str(v['cash_in']-v['cash_out']) if cash_ready else None}
    reconciliation=await quality(db)
    monthly=[];running_result=0;running_cash=0
    for period,values in sorted(months.items()):
        running_result+=values['revenue']-values['expense']-values['consumption']
        running_cash+=values['cash_in']-values['cash_out']
        monthly.append({'period':period,**serialize(values),
            'cumulative_result_fcfa':str(running_result) if ready else None,
            'cumulative_cash_fcfa':str(running_cash) if cash_ready else None})
    by_activity=[]
    activity_month_values={a.id:defaultdict(int) for a in activities}
    for activity in sorted(activities,key=lambda a:a.name):
        values=per_activity[activity.id]
        running=0;before=0;low=0;before_low=0
        for day,day_values in sorted(activity_dates[activity.id].items()):
            delta=day_values['cash_in']-day_values['cash_out']
            running+=delta
            before+=delta-day_values['funding_in']+day_values['funding_out']
            low=min(low,running);before_low=min(before_low,before)
            activity_month_values[activity.id][day[:7]]+=delta-day_values['funding_in']+day_values['funding_out']
        result=values['revenue']-values['expense']-values['consumption']
        status='À vérifier' if not ready or not cash_ready else 'Déficitaire' if result<0 else 'Trésorerie à soutenir' if running<0 else 'Excédentaire'
        by_activity.append({'activity_id':activity.id,'name':activity.name,'demo_dataset':activity.demo_dataset,
            'campaign_count':sum(c.activity_id==activity.id for c in campaigns),**serialize(values),
            'cash_min_fcfa':str(low) if cash_ready else None,'funding_gap_fcfa':str(-before_low) if cash_ready else None,'status':status})
    # Une seule chronologie mensuelle, y compris les mois sans nouvelle source.
    activity_monthly=[];activity_running={a.id:0 for a in activities}
    if months:
        cursor=date.fromisoformat(min(months)+'-01')
        while cursor.strftime('%Y-%m')<=as_of.strftime('%Y-%m'):
            period=cursor.strftime('%Y-%m');row={'period':period}
            for activity in activities:
                activity_running[activity.id]+=activity_month_values[activity.id][period]
                row[f'activity_{activity.id}']=str(activity_running[activity.id]) if cash_ready else None
            activity_monthly.append(row)
            cursor=date(cursor.year+1,1,1) if cursor.month==12 else date(cursor.year,cursor.month+1,1)
    return {'campaign_ids':ids,'campaigns':[campaign_json(c) for c in campaigns],'currency':'XOF','as_of':as_of.isoformat(),
        'scope':'Sources explicitement rattachées uniquement ; aucune reprise automatique de l’historique.',
        'totals':serialize(totals),'monthly':monthly,
        'yearly':[{'period':k,**serialize(v)} for k,v in sorted(years.items())],
        'by_campaign':[{'campaign_id':c.id,'activity_id':c.activity_id,'name':c.name,**serialize(per_campaign[c.id])} for c in campaigns],
        'by_activity':by_activity,'activity_monthly':activity_monthly,'demo_dataset':next(iter(datasets),None),
        'quality':{'result_available':ready,'cash_available':cash_ready,'issues':issues,'unassigned_global':reconciliation['unassigned_total'],
                   'status':'À vérifier' if issues or reconciliation['unassigned_total'] else 'Sources rattachées cohérentes',
                   'note':'Les achats ne sont pas des charges ; les paiements ne sont pas additionnés aux ventes et dépenses. Charges communes et complétude métier restent à valider.'},
        'sources':sources}


async def declare_opening_cost(db,product_id,request,actor):
    h=fingerprint({'product_id':product_id,**request.model_dump(mode='json'),'actor_id':actor})
    try:
        await lock_key(db,'valuation-command:'+str(request.client_operation_id))
        old=await db.scalar(select(ProductValuation).where(ProductValuation.client_operation_id==str(request.client_operation_id)))
        if old:
            if old.payload_hash!=h:raise HTTPException(409,'Commande réutilisée avec un autre contenu.')
            return {'id':str(old.id),'product_id':old.product_id,'basis':old.basis,'unit_cost':str(old.unit_cost)}
        product=await db.scalar(select(Product).where(Product.id==product_id).with_for_update().execution_options(populate_existing=True))
        if product is None:raise HTTPException(404,'Produit introuvable.')
        if product.current_stock!=request.expected_quantity:raise HTTPException(409,'La quantité a changé ; refaire le contrôle de valorisation.')
        if product.cost_basis!='UNVERIFIED':raise HTTPException(409,'Coût déjà vérifié. Une correction documentée distincte est nécessaire.')
        product.unit_price=request.unit_cost;product.cost_basis='DECLARED'
        event=ProductValuation(product_id=product.id,quantity=product.current_stock,unit_cost=request.unit_cost,basis='DECLARED',
            origin='OPENING',client_operation_id=str(request.client_operation_id),payload_hash=h,reason=request.reason,actor_id=actor)
        db.add(event);await db.commit();await db.refresh(event)
        return {'id':str(event.id),'product_id':product_id,'basis':'DECLARED','unit_cost':str(event.unit_cost)}
    except Exception:
        await db.rollback();raise


async def require_unassigned(db,kind,source_id):
    """Une source validée pour une campagne se corrige par libération motivée."""
    await lock_key(db,f'{kind}:{source_id}')
    latest=await db.scalar(terminal_query().where(CampaignEvent.source_type==kind,CampaignEvent.source_id==source_id))
    if latest and latest.action=='ASSIGN':
        raise HTTPException(409,'Source rattachée à une campagne : libérer explicitement son affectation avant correction.')
    await source_row(db,kind,source_id,lock=True)
    if kind=='FEED':
        linked=(await db.scalars(select(StockMovement.id).where(StockMovement.reference_type=='FeedRecord',StockMovement.reference_id==source_id).order_by(StockMovement.id))).all()
        for movement_id in linked:
            await require_unassigned(db,'STOCK',movement_id)
