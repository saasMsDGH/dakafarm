"""Rapprochements et indicateurs avicoles issus des mêmes pièces de campagne."""
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select, func
from app.api.v1.campaigns.poultry_models import PoultryCampaign, PayrollAllocation
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.hr.models.payroll_payment import PayrollPayment
from app.api.v1.hr.models.employee import Employee
from app.api.v1.pos.models.sale import SaleItem
from app.api.v1.pos.models.purchase import PurchaseItem


def percent(value,capital):
    return str((Decimal(value)*100/Decimal(capital)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)) if capital else None


async def validate_payroll(db,sources,issues):
    allocations=[e for e in sources if e['source_type']=='PAYROLL_ALLOC']
    by_key={(int(e['snapshot']['data']['payroll_id']),e['campaign_id']):e for e in allocations}
    ids={key[0] for key in by_key}
    payrolls={p.id:p for p in (await db.scalars(select(Payroll).where(Payroll.id.in_(ids)))).all()} if ids else {}
    totals=dict((await db.execute(select(PayrollAllocation.payroll_id,func.sum(PayrollAllocation.amount_fcfa)).where(PayrollAllocation.payroll_id.in_(ids)).group_by(PayrollAllocation.payroll_id))).all()) if ids else {}
    for event in allocations:
        raw=event['snapshot']['data'];pid=int(raw['payroll_id']);p=payrolls.get(pid)
        if not p or p.employee_id!=raw['employee_id'] or p.pay_period!=raw['pay_period'] or p.net_salary!=Decimal(raw['payroll_net_fcfa']) or totals.get(pid)!=p.net_salary or raw['campaign_id']!=event['campaign_id']:
            issues.append({'event_id':event['id'],'source_type':'PAYROLL_ALLOC','source_id':event['source_id'],'type':'PAYROLL_RECONCILIATION_REQUIRED'})
    cash=[e for e in sources if e['source_type']=='CASH' and e['snapshot']['data']['transaction_type']=='PAYROLL']
    refs=[e['snapshot']['data']['reference_number'] for e in cash]
    payments={p.payment_reference:p for p in (await db.scalars(select(PayrollPayment).where(PayrollPayment.payment_reference.in_(refs)))).all()} if refs else {}
    seen=set()
    for event in cash:
        raw=event['snapshot']['data'];ref=raw['reference_number'];p=payments.get(ref)
        allocation=by_key.get((p.payroll_id,event['campaign_id'])) if p else None
        valid=p is not None and allocation is not None and raw['direction']=='OUT' and raw['account_id']==p.account_id and Decimal(raw['amount'])==p.amount==Decimal(allocation['snapshot']['data']['amount_fcfa'])
        if not valid or ref in seen:
            issues.append({'event_id':event['id'],'source_type':'CASH','source_id':event['source_id'],'type':'PAYROLL_RECONCILIATION_REQUIRED'})
        seen.add(ref)


async def poultry_summary(db,sources,by_campaign,campaigns,as_of,issues):
    maps=list((await db.scalars(select(PoultryCampaign).where(PoultryCampaign.campaign_id.in_([c.id for c in campaigns])))).all())
    if not maps:return None
    mapping={p.campaign_id:p for p in maps};selected=[e for e in sources if e['campaign_id'] in mapping]
    sales=[e['source_id'] for e in selected if e['source_type']=='SALE'];purchases=[e['source_id'] for e in selected if e['source_type']=='PURCHASE']
    sale_items=defaultdict(list);purchase_items=defaultdict(list)
    for item in (await db.scalars(select(SaleItem).where(SaleItem.sale_id.in_(sales)))).all():sale_items[item.sale_id].append(item)
    for item in (await db.scalars(select(PurchaseItem).where(PurchaseItem.purchase_id.in_(purchases)))).all():purchase_items[item.purchase_id].append(item)
    fields=['birds_bought','deaths','hens_sold','eggs_produced','damaged_eggs','eggs_sold','egg_revenue','hen_revenue','bird_purchase','feed_purchase','vaccine_purchase','feed_cost','vaccine_cost','wages','other_cost','mortality_cost','cash_flow']
    values={cid:{k:0 for k in fields} for cid in mapping};monthly=defaultdict(lambda:{k:0 for k in fields});cash_days={cid:defaultdict(int) for cid in mapping}
    stocks=defaultdict(list)
    for event in selected:
        if event['source_type']=='STOCK':
            r=event['snapshot']['data'];stocks[(r.get('reference_type'),r.get('reference_id'))].append(event)
    def issue(event,code):issues.append({'event_id':event['id'],'source_type':event['source_type'],'source_id':event['source_id'],'type':code})
    for event in selected:
        p=mapping[event['campaign_id']];v=values[event['campaign_id']];raw=event['snapshot']['data'];kind=event['source_type'];delta=defaultdict(int)
        if kind=='PURCHASE':
            items=purchase_items[event['source_id']]
            if sum(i.total_amount for i in items)!=Decimal(raw['total_amount']):issue(event,'POULTRY_RECONCILIATION_REQUIRED')
            for i in items:
                key={p.bird_product_id:'bird_purchase',p.feed_product_id:'feed_purchase',p.vaccine_product_id:'vaccine_purchase'}.get(i.product_id)
                if key:delta[key]+=int(i.total_amount)
                if i.product_id==p.bird_product_id:delta['birds_bought']+=int(i.quantity)
        elif kind=='SALE':
            items=sale_items[event['source_id']]
            if sum(i.total_amount for i in items)!=Decimal(raw['total_amount']):issue(event,'POULTRY_RECONCILIATION_REQUIRED')
            for i in items:
                outs=[e for e in stocks[('Sale',event['source_id'])] if e['snapshot']['data']['product_id']==i.product_id]
                if sum(Decimal(e['snapshot']['data']['quantity']) for e in outs)!=i.quantity:issue(event,'POULTRY_RECONCILIATION_REQUIRED')
                if i.product_id==p.egg_product_id:delta['eggs_sold']+=int(i.quantity);delta['egg_revenue']+=int(i.total_amount)
                elif i.product_id==p.bird_product_id:delta['hens_sold']+=int(i.quantity);delta['hen_revenue']+=int(i.total_amount)
        elif kind=='PRODUCTION':
            delta['eggs_produced']+=int(raw['good_eggs']);delta['damaged_eggs']+=int(raw['damaged_eggs'])
            ins=[e for e in stocks[('ProductionRecord',event['source_id'])] if e['snapshot']['data']['product_id']==p.egg_product_id and e['snapshot']['data']['movement_type']=='IN']
            if sum(Decimal(e['snapshot']['data']['quantity']) for e in ins)!=int(raw['good_eggs']):issue(event,'POULTRY_RECONCILIATION_REQUIRED')
        elif kind=='MORTALITY':delta['deaths']+=int(raw['quantity'])
        elif kind=='PAYROLL_ALLOC':delta['wages']+=int(raw['amount_fcfa'])
        elif kind=='EXPENSE':delta['other_cost']+=int(raw['amount'])
        elif kind=='STOCK' and raw['movement_type']=='OUT':
            key={p.feed_product_id:'feed_cost',p.vaccine_product_id:'vaccine_cost'}.get(raw['product_id'])
            if key:delta[key]+=int(raw['cost_total_fcfa'] or 0)
            if raw['product_id']==p.bird_product_id and raw['reference_type']=='MortalityRecord':delta['mortality_cost']+=int(raw['cost_total_fcfa'] or 0)
        elif kind=='CASH' and raw['transaction_type']!='OWNER_INVESTMENT':
            delta['cash_flow']=int(raw['amount'])*(1 if raw['direction']=='IN' else -1)
            cash_days[event['campaign_id']][event['snapshot']['date']]+=delta['cash_flow']
        for k,amount in delta.items():v[k]+=amount;monthly[event['snapshot']['date'][:7]][k]+=amount
    rows=[];campaign_names={c.id:c.name for c in campaigns};finance={r['campaign_id']:r for r in by_campaign}
    ready=not issues
    for cid,p in mapping.items():
        v=values[cid];v['birds_remaining']=v['birds_bought']-v['deaths']-v['hens_sold'];v['eggs_remaining']=v['eggs_produced']-v['eggs_sold']
        if v['birds_remaining']<0 or v['eggs_remaining']<0:
            issues.append({'event_id':'0','source_type':'PRODUCTION','source_id':p.flock_id,'type':'POULTRY_RECONCILIATION_REQUIRED'});ready=False
        capital=int(finance[cid]['funding_in']);cash=int(finance[cid]['cash_before_funding_fcfa'] or 0)
        running=0;started=False;payback=None
        for day,amount in sorted(cash_days[cid].items()):
            running+=amount
            if running<0:started=True
            if started and running>=0 and payback is None:payback=day
        rows.append({'campaign_id':cid,'flock_id':p.flock_id,'name':campaign_names[cid],**{k:str(n) for k,n in v.items()},
            'capital_fcfa':str(capital),'cash_before_funding_fcfa':str(cash),'management_result_fcfa':finance[cid]['result_fcfa'] if ready else None,
            'cash_roi_percent':percent(cash,capital) if ready else None,'payback_date':payback if ready else None,'assumptions':p.assumptions})
    employee_ids={e['snapshot']['data']['employee_id'] for e in selected if e['source_type']=='PAYROLL_ALLOC'}
    employees=list((await db.scalars(select(Employee).where(Employee.id.in_(employee_ids)).order_by(Employee.employee_code))).all()) if employee_ids else []
    capital_total=sum(int(r['capital_fcfa']) for r in rows);cash_total=sum(int(r['cash_before_funding_fcfa']) for r in rows)
    monthly_rows=[];running=0
    for period,value in sorted(monthly.items()):
        running+=value['cash_flow'];monthly_rows.append({'period':period,**{k:str(v) for k,v in value.items()},'cumulative_cash_fcfa':str(running)})
    payroll_ids={e['snapshot']['data']['payroll_id'] for e in selected if e['source_type']=='PAYROLL_ALLOC'}
    salaries=list((await db.scalars(select(Payroll.net_salary).where(Payroll.id.in_(payroll_ids)))).all()) if payroll_ids else []
    mean=str(sum(salaries)/len(salaries)) if salaries else None
    return {'campaigns':rows,'monthly':monthly_rows,'capital_fcfa':str(capital_total),'cash_roi_percent':percent(cash_total,capital_total) if ready else None,
        'salary_mean_fcfa':str(int(Decimal(mean))) if mean else None,'customer_count':len({e['snapshot']['data']['customer_id'] for e in selected if e['source_type']=='SALE'}),
        'employee_count':len(employees),'employees':[{'id':e.id,'name':e.first_name+' '+e.last_name,'position':e.position} for e in employees],
        'note':'ROI de trésorerie réalisé = flux hors apports / fonds apportés. Pas de rendement futur présumé. Coûts salariaux hors cotisations patronales non paramétrées. Les charges de ponte sont reconnues directement ; la sortie des œufs ne les déduit pas à nouveau.'}
