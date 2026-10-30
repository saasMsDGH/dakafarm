from datetime import date, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.RoleAuth import RoleChecker
from app.core.database import get_db
from app.api.v1.user.models import Users
from app.api.v1.campaigns.models import Activity, Campaign, CampaignEvent
from app.api.v1.campaigns.schemas import ActivityCreate, CampaignCreate, AssignmentCreate, ReleaseCreate, OpeningValuation, SourceType
from app.api.v1.campaigns import service
from app.api.v1.inventory.models.product import Product

router=APIRouter(prefix='/campaign-data',tags=['Campagnes et validation des données'])
reader=RoleChecker(['finance_manager'])
admin=RoleChecker(['admin'])
DB=Annotated[AsyncSession,Depends(get_db)]
Reader=Annotated[Users,Depends(reader)]
Admin=Annotated[Users,Depends(admin)]


@router.get('/activities')
async def activities(db:DB,user:Reader):
    return [service.activity_json(x) for x in (await db.scalars(select(Activity).order_by(Activity.name))).all()]


@router.post('/activities',status_code=201)
async def activity_create(request:ActivityCreate,db:DB,user:Admin):
    return await service.create_activity(db,request,user.id)


@router.get('/campaigns')
async def campaigns(db:DB,user:Reader):
    return [service.campaign_json(x) for x in (await db.scalars(select(Campaign).order_by(Campaign.start_date.desc(),Campaign.id))).all()]


@router.post('/campaigns',status_code=201)
async def campaign_create(request:CampaignCreate,db:DB,user:Admin):
    return await service.create_campaign(db,request,user.id)


@router.get('/quality')
async def quality(db:DB,user:Reader):return await service.quality(db)


@router.get('/sources/{kind}')
async def sources(kind:SourceType,db:DB,user:Reader,limit:int=Query(50,ge=1,le=100),before_id:int|None=Query(None,gt=0)):
    return await service.list_sources(db,kind,limit,before_id)


@router.post('/campaigns/{campaign_id}/assignments',status_code=201)
async def assign(campaign_id:int,request:AssignmentCreate,db:DB,user:Reader):
    return await service.assign(db,campaign_id,request,user.id)


@router.post('/events/{event_id}/release',status_code=201)
async def release(event_id:int,request:ReleaseCreate,db:DB,user:Reader):
    return await service.release(db,event_id,request,user.id)


@router.get('/events')
async def events(db:DB,user:Reader,campaign_id:int|None=Query(None,gt=0),before_id:int|None=Query(None,gt=0),limit:int=Query(50,ge=1,le=100)):
    q=select(CampaignEvent).order_by(CampaignEvent.id.desc()).limit(limit+1)
    if campaign_id:q=q.where(CampaignEvent.campaign_id==campaign_id)
    if before_id:q=q.where(CampaignEvent.id<before_id)
    rows=list((await db.scalars(q)).all())
    return {'items':[service.event_json(e) for e in rows[:limit]],'next_cursor':str(rows[limit-1].id) if len(rows)>limit else None}


@router.get('/report')
async def report(db:DB,user:Reader,campaign_ids:Annotated[list[int],Query(min_length=1,max_length=50)],as_of:date|None=None):
    return await service.report(db,campaign_ids,as_of or datetime.now(timezone.utc).date())


@router.get('/valuation/products')
async def product_valuations(db:DB,user:Reader,limit:int=Query(50,ge=1,le=100),before_id:int|None=Query(None,gt=0)):
    q=select(Product).order_by(Product.id.desc()).limit(limit+1)
    if before_id:q=q.where(Product.id<before_id)
    rows=list((await db.scalars(q)).all())
    return {'items':[{'id':p.id,'name':p.name,'quantity':str(p.current_stock),'unit':p.unit_of_measure,
        'unit_cost':str(p.unit_price),'cost_basis':p.cost_basis} for p in rows[:limit]],
        'next_cursor':rows[limit-1].id if len(rows)>limit else None}


@router.post('/valuation/products/{product_id}',status_code=201)
async def opening_valuation(product_id:int,request:OpeningValuation,db:DB,user:Admin):
    return await service.declare_opening_cost(db,product_id,request,user.id)
