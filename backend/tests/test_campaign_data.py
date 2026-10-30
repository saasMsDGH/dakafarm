"""Contrats métier vérifiés sur PostgreSQL jetable, sans données ni secrets du cluster."""
import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import os
import time
import unittest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
import urllib.request
import urllib.parse
import urllib.error
from fastapi import HTTPException
from sqlalchemy import select, text, func
from sqlalchemy.exc import DBAPIError
import app.db
from app.core.database import engine, sessionlocal
from app.api.v1.user.models import Users, Roles, UserRole
from app.api.v1.campaigns import service as svc
from app.api.v1.campaigns.models import CampaignEvent, ProductValuation
from app.api.v1.campaigns.schemas import ActivityCreate, CampaignCreate, AssignmentCreate, ReleaseCreate, OpeningValuation
from app.api.v1.campaigns.sources import project, fingerprint, measures
from app.api.v1.inventory.models.product import Product
from app.api.v1.inventory.models.product_category import ProductCategory
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.inventory.schemas.StockMovementSchema import StockMovementCreate
from app.api.v1.inventory.service.StockMovementService import StockMovementService
from app.api.v1.pos.models.expense import Expense
from app.api.v1.pos.models.expense_payment import ExpensePayment
from app.api.v1.pos.models.sale import Sale
from app.api.v1.pos.models.customer import Customer
from app.api.v1.pos.models.supplier import Supplier
from app.api.v1.pos.models.purchase import Purchase
from app.api.v1.pos.schemas.PurchaseSchema import PurchaseCreate
from app.api.v1.pos.service.PurchaseService import PurchaseService
from app.api.v1.finance.models.account import FinancialAccount
from app.api.v1.finance.models.transaction import FinancialTransaction
from app.api.v1.farm.models.house import House
from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.feed_record import FeedRecord
from app.api.v1.farm.schemas.FeedRecordSchema import FeedRecordCreate, FeedRecordUpdate
from app.api.v1.farm.service.FeedRecordService import FeedRecordService

WHEN=datetime(2025,6,1,tzinfo=timezone.utc)

def code():return uuid4().hex.upper()

class CampaignDataTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db=sessionlocal()
        self.actor=await self.db.scalar(select(Users.id).where(Users.email==os.environ['TEST_ADMIN_EMAIL']))
        activity=await svc.create_activity(self.db,ActivityCreate(code=code(),name='Aviculture recette'),self.actor)
        self.campaign=await svc.create_campaign(self.db,CampaignCreate(activity_id=activity['id'],code=code(),name='Campagne 2025–2027',start_date=date(2025,1,1),end_date=date(2027,12,31)),self.actor)
        self.cid=self.campaign['id']

    async def asyncTearDown(self):
        await self.db.close()
        await engine.dispose()

    async def save(self,row):
        self.db.add(row);await self.db.commit();await self.db.refresh(row)
        return row

    async def expense(self,amount='1000',when=WHEN):
        return await self.save(Expense(expense_number=code(),category='Transport',amount=Decimal(amount),expense_date=when))

    async def product(self,quantity='10',cost='1000',basis='UNVERIFIED'):
        category=await self.save(ProductCategory(name=code()))
        return await self.save(Product(category_id=category.id,name='Aliment recette',unit_of_measure='kg',current_stock=Decimal(quantity),unit_price=Decimal(cost),cost_basis=basis))

    def command(self,kind,row):
        return AssignmentCreate(client_operation_id=uuid4(),source_type=kind,source_id=row.id,source_hash=fingerprint(project(kind,row)),confirm_currency='XOF',reason='Contrôle pièce justificative en XOF')

    async def attach(self,kind,row,cid=None):
        await self.db.refresh(row)
        return await svc.assign(self.db,cid or self.cid,self.command(kind,row),self.actor)

    async def report(self,asof=date(2027,12,31),ids=None):
        return await svc.report(self.db,ids or [self.cid],asof)

    async def test_multiyear_accrual_cash_and_purchase_not_doubled(self):
        e1=await self.expense('1000');eid=e1.id;await self.attach('EXPENSE',e1)
        e2=await self.expense('2000',datetime(2026,1,2,tzinfo=timezone.utc));await self.attach('EXPENSE',e2)
        supplier=await self.save(Supplier(supplier_code=code(),name='Fournisseur recette'))
        purchase=await self.save(Purchase(purchase_number=code(),supplier_id=supplier.id,total_amount=5000,purchase_date=WHEN))
        await self.attach('PURCHASE',purchase)
        account=await self.save(FinancialAccount(name=code(),account_type='CASH'))
        aid=account.id;ref=code()
        await self.save(ExpensePayment(expense_id=eid,account_id=aid,payment_reference=ref,amount=1000,payment_method='Cash',payment_date=WHEN))
        cash=await self.save(FinancialTransaction(account_id=aid,transaction_type='EXPENSE',direction='OUT',amount=1000,reference_number=ref,transaction_date=WHEN))
        await self.attach('CASH',cash)
        report=await self.report(ids=[self.cid,self.cid]);self.assertEqual(report['totals']['result_fcfa'],'-3000')
        self.assertEqual(report['totals']['cash_net_fcfa'],'-1000')
        self.assertEqual([r['period'] for r in report['yearly']],['2025','2026'])
        self.assertEqual([r['cumulative_result_fcfa'] for r in report['monthly']],['-1000','-3000'])
        early=await self.report(date(2025,12,31));self.assertEqual(early['totals']['expense'],'1000')

    async def test_idempotency_conflict_and_explicit_release_chain(self):
        row=await self.expense();req=self.command('EXPENSE',row)
        e=await svc.assign(self.db,self.cid,req,self.actor)
        self.assertEqual((await svc.assign(self.db,self.cid,req,self.actor))['id'],e['id'])
        with self.assertRaises(HTTPException) as error:
            await svc.assign(self.db,self.cid,req.model_copy(update={'reason':'Autre contenu'}),self.actor)
        self.assertEqual(error.exception.status_code,409)
        release=await svc.release(self.db,int(e['id']),ReleaseCreate(client_operation_id=uuid4(),reason='Correction documentée'),self.actor)
        self.assertEqual(release['previous_event_id'],e['id'])
        self.assertEqual((await self.report())['totals']['expense'],'0')
        again=await self.attach('EXPENSE',row);self.assertEqual(again['previous_event_id'],release['id'])
        self.assertEqual((await self.report())['totals']['expense'],'1000')

    async def test_concurrent_assignment_has_one_winner(self):
        row=await self.expense();req=self.command('EXPENSE',row)
        async def attempt():
            async with sessionlocal() as db:
                try:await svc.assign(db,self.cid,req.model_copy(update={'client_operation_id':uuid4()}),self.actor);return 201
                except HTTPException as err:return err.status_code
        self.assertEqual(sorted(await asyncio.gather(attempt(),attempt())),[201,409])

    async def test_fingerprint_refuses_stale_confirmation_and_detects_sql_drift(self):
        row=await self.expense();req=self.command('EXPENSE',row)
        row.amount=2000;await self.db.commit()
        with self.assertRaises(HTTPException) as error:await svc.assign(self.db,self.cid,req,self.actor)
        self.assertEqual(error.exception.status_code,409)
        await self.db.refresh(row);await self.attach('EXPENSE',row)
        await self.db.refresh(row)
        await self.db.execute(text('UPDATE expenses SET amount=3000 WHERE id=:id'),{'id':row.id});await self.db.commit()
        report=await self.report();self.assertIsNone(report['totals']['result_fcfa'])
        self.assertEqual(report['quality']['issues'][0]['type'],'SOURCE_CHANGED')
        self.assertEqual(report['totals']['expense'],'2000')

    async def test_deleted_source_is_visible_and_blocks_result(self):
        row=await self.expense();await self.attach('EXPENSE',row);await self.db.delete(row);await self.db.commit()
        report=await self.report();self.assertIsNone(report['totals']['result_fcfa'])
        self.assertEqual(report['quality']['issues'][0]['type'],'SOURCE_MISSING')

    async def test_fractional_negative_and_outside_dates_refused(self):
        for amount in ['12.50','-5']:
            row=await self.expense(amount)
            with self.assertRaises(HTTPException) as error:await self.attach('EXPENSE',row)
            self.assertEqual(error.exception.status_code,422)
        row=await self.expense('100',datetime(2024,1,1,tzinfo=timezone.utc))
        with self.assertRaises(HTTPException) as error:await self.attach('EXPENSE',row)
        self.assertEqual(error.exception.status_code,422)

    async def test_audit_rows_immutable_and_branch_rejected_in_database(self):
        row=await self.expense();e=await self.attach('EXPENSE',row)
        for statement in ['UPDATE campaign_events SET reason=reason WHERE id=:id','DELETE FROM campaign_events WHERE id=:id']:
            with self.assertRaises(DBAPIError):await self.db.execute(text(statement),{'id':int(e['id'])})
            await self.db.rollback()
        with self.assertRaises(DBAPIError):await self.db.execute(text('TRUNCATE campaign_events CASCADE'))
        await self.db.rollback()
        sql='''INSERT INTO campaign_events(campaign_id,source_type,source_id,action,client_operation_id,payload_hash,source_hash,snapshot,reason,actor_id)
               SELECT campaign_id,source_type,source_id,action,:op,payload_hash,source_hash,snapshot,reason,actor_id FROM campaign_events WHERE id=:id'''
        with self.assertRaises(DBAPIError):await self.db.execute(text(sql),{'id':int(e['id']),'op':str(uuid4())})
        await self.db.rollback()

    async def test_unvalued_stock_never_shows_profit_and_opening_does_not_rewrite_it(self):
        product=await self.product();pid=product.id
        movement=await StockMovementService.create(self.db,StockMovementCreate(product_id=pid,movement_type='OUT',quantity=2,reference_type='FeedRecord',reference_id=999,movement_date=WHEN),self.actor)
        mid=movement.id;await self.attach('STOCK',movement)
        self.assertIsNone((await self.report())['totals']['result_fcfa'])
        req=OpeningValuation(client_operation_id=uuid4(),expected_quantity=8,unit_cost=1100,confirm_currency='XOF',reason='Inventaire contrôlé justificatif')
        val=await svc.declare_opening_cost(self.db,pid,req,self.actor)
        self.assertEqual((await svc.declare_opening_cost(self.db,pid,req,self.actor))['id'],val['id'])
        await self.db.refresh(movement);self.assertIsNone(movement.cost_total_fcfa)
        with self.assertRaises(DBAPIError):await self.db.execute(text('DELETE FROM product_valuations WHERE id=:id'),{'id':int(val['id'])})
        await self.db.rollback()
        new=await StockMovementService.create(self.db,StockMovementCreate(product_id=pid,movement_type='OUT',quantity=2,reference_type='FeedRecord',reference_id=998,movement_date=WHEN),self.actor)
        self.assertEqual(new.cost_total_fcfa,2200)

    async def test_purchase_weighted_average_and_discount(self):
        product=await self.product(basis='DECLARED');pid=product.id
        supplier=await self.save(Supplier(supplier_code=code(),name='Fournisseur recette'));sid=supplier.id
        request=PurchaseCreate(supplier_id=sid,discount=2000,items=[{'product_id':pid,'quantity':10,'unit_cost':1400}])
        await PurchaseService.create(self.db,request,self.actor)
        await self.db.refresh(product)
        self.assertEqual(product.current_stock,Decimal('20'))
        self.assertEqual(product.unit_price,Decimal('1100'))
        self.assertEqual(product.cost_basis,'WEIGHTED_AVERAGE')
        movement=await StockMovementService.create(self.db,StockMovementCreate(product_id=pid,movement_type='OUT',quantity=3,reference_type='Sale',reference_id=999,movement_date=WHEN),self.actor)
        self.assertEqual(movement.cost_total_fcfa,3300)

    async def test_existing_unverified_stock_remains_unverified_after_purchase(self):
        product=await self.product();pid=product.id
        supplier=await self.save(Supplier(supplier_code=code(),name='Fournisseur recette'))
        await PurchaseService.create(self.db,PurchaseCreate(supplier_id=supplier.id,items=[{'product_id':pid,'quantity':5,'unit_cost':1200}]),self.actor)
        await self.db.refresh(product);self.assertEqual(product.cost_basis,'UNVERIFIED')

    async def test_concurrent_stock_out_cannot_overspend_stock(self):
        product=await self.product(quantity='10',basis='DECLARED');pid=product.id
        async def out():
            async with sessionlocal() as db:
                try:await StockMovementService.create(db,StockMovementCreate(product_id=pid,movement_type='OUT',quantity=7),self.actor);return 201
                except HTTPException as err:await db.rollback();return err.status_code
        self.assertEqual(sorted(await asyncio.gather(out(),out())),[201,400])
        await self.db.refresh(product);self.assertEqual(product.current_stock,Decimal('3'))

    async def flock(self):
        house=await self.save(House(name=code(),capacity=100))
        return await self.save(Flock(flock_code=code(),house_id=house.id,initial_quantity=10,current_quantity=10,arrival_date=date(2025,1,1)))

    async def test_feed_creation_rolls_back_record_when_stock_step_fails(self):
        product=await self.product();pid=product.id;flock=await self.flock();fid=flock.id
        before=await self.db.scalar(select(func.count()).select_from(FeedRecord))
        with patch.object(StockMovementService,'create',new=AsyncMock(side_effect=RuntimeError('Panne simulée'))):
            with self.assertRaises(HTTPException):await FeedRecordService.create(self.db,FeedRecordCreate(flock_id=fid,product_id=pid,record_date=date(2025,6,1),quantity_used=2),self.actor)
        self.assertEqual(await self.db.scalar(select(func.count()).select_from(FeedRecord)),before)
        await self.db.refresh(product);self.assertEqual(product.current_stock,Decimal('10'))

    async def test_feed_update_rolls_back_partial_stock_restoration(self):
        product=await self.product(basis='DECLARED');pid=product.id;flock=await self.flock();fid=flock.id
        record=await FeedRecordService.create(self.db,FeedRecordCreate(flock_id=fid,product_id=pid,record_date=date(2025,6,1),quantity_used=2),self.actor)
        rid=record.id
        count=await self.db.scalar(select(func.count()).select_from(StockMovement))
        with self.assertRaises(HTTPException):
            await FeedRecordService.update(self.db,rid,FeedRecordUpdate(product_id=2147483647),self.actor)
        await self.db.refresh(product);await self.db.refresh(record)
        self.assertEqual(product.current_stock,Decimal('8'));self.assertEqual(product.cost_basis,'DECLARED')
        self.assertEqual(record.product_id,pid)
        self.assertEqual(await self.db.scalar(select(func.count()).select_from(StockMovement)),count)

    async def test_multiple_activities_campaigns_and_repeated_selection(self):
        first=await self.expense('700');await self.attach('EXPENSE',first)
        other=await svc.create_activity(self.db,ActivityCreate(code=code(),name='Commerce recette'),self.actor)
        campaign=await svc.create_campaign(self.db,CampaignCreate(activity_id=other['id'],code=code(),name='Commerce 2025',start_date=date(2025,1,1)),self.actor)
        second=await self.expense('300');await self.attach('EXPENSE',second,campaign['id'])
        report=await self.report(ids=[self.cid,campaign['id'],campaign['id']])
        self.assertEqual(report['totals']['expense'],'1000');self.assertEqual(len(report['sources']),2)
        self.assertEqual(len(report['by_campaign']),2)

    async def test_feed_stock_date_and_freeze_when_stock_assigned(self):
        product=await self.product(basis='DECLARED');pid=product.id;flock=await self.flock();fid=flock.id
        record=await FeedRecordService.create(self.db,FeedRecordCreate(flock_id=fid,product_id=pid,record_date=date(2025,6,1),quantity_used=2),self.actor)
        rid=record.id
        movement=await self.db.scalar(select(StockMovement).where(StockMovement.reference_type=='FeedRecord',StockMovement.reference_id==rid))
        self.assertEqual(movement.movement_date.date(),date(2025,6,1))
        await self.attach('FEED',record)
        self.assertIsNone((await self.report())['totals']['result_fcfa'])
        await self.attach('STOCK',movement)
        self.assertEqual((await self.report())['totals']['result_fcfa'],'-2000')
        with self.assertRaises(HTTPException) as error:await FeedRecordService.update(self.db,rid,FeedRecordUpdate(quantity_used=1),self.actor)
        self.assertEqual(error.exception.status_code,409)

    async def test_unknown_cash_economics_block_result_but_keep_cash_chart(self):
        account=await self.save(FinancialAccount(name=code(),account_type='CASH'))
        cash=await self.save(FinancialTransaction(account_id=account.id,transaction_type='PAYROLL',direction='OUT',amount=500,transaction_date=WHEN))
        await self.attach('CASH',cash)
        report=await self.report();self.assertIsNone(report['totals']['result_fcfa'])
        self.assertEqual(report['totals']['cash_net_fcfa'],'-500')

    async def test_cash_without_matching_document_blocks_economic_result(self):
        account=await self.save(FinancialAccount(name=code(),account_type='CASH'))
        cash=await self.save(FinancialTransaction(account_id=account.id,transaction_type='SALE',direction='IN',amount=800,transaction_date=WHEN))
        await self.attach('CASH',cash)
        report=await self.report();self.assertIsNone(report['totals']['result_fcfa'])
        self.assertEqual(report['totals']['cash_net_fcfa'],'800')
        self.assertIn('CASH_DOCUMENT_LINK_REQUIRED',[x['type'] for x in report['quality']['issues']])

    async def test_sale_requires_linked_stock_assignment_for_margin(self):
        customer=await self.save(Customer(customer_code=code(),name='Client recette'))
        sale=await self.save(Sale(invoice_number=code(),customer_id=customer.id,total_amount=5000,sale_date=WHEN))
        saleid=sale.id;await self.attach('SALE',sale)
        self.assertIsNone((await self.report())['totals']['result_fcfa'])
        product=await self.product(basis='DECLARED')
        movement=await StockMovementService.create(self.db,StockMovementCreate(product_id=product.id,movement_type='OUT',quantity=2,reference_type='Sale',reference_id=saleid,movement_date=WHEN),self.actor)
        await self.attach('STOCK',movement)
        self.assertEqual((await self.report())['totals']['result_fcfa'],'3000')

    async def test_database_user_is_not_superuser(self):
        flags=(await self.db.execute(text('SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user'))).one()
        self.assertFalse(any(flags))

    async def test_migration_preserves_legacy_amount_quantity_and_unknown_currency(self):
        legacy=await self.db.scalar(select(Product).where(Product.name=='MIGRATION_LEGACY'))
        self.assertEqual(legacy.unit_price,Decimal('123.45'))
        self.assertEqual(legacy.current_stock,Decimal('12.345'))
        self.assertEqual(legacy.cost_basis,'UNVERIFIED')
        self.assertGreaterEqual((await svc.quality(self.db))['unassigned_total'],1)

class ApiTests(unittest.TestCase):
    @classmethod
    def request(cls,path,data=None,token=None,form=False):
        headers={}
        if token:headers['Authorization']='Bearer '+token
        if data is not None:
            data=(urllib.parse.urlencode(data) if form else json.dumps(data)).encode()
            headers['Content-Type']='application/x-www-form-urlencoded' if form else 'application/json'
        try:
            with urllib.request.urlopen(urllib.request.Request(os.environ['TEST_API_URL']+path,data=data,headers=headers),timeout=10) as r:
                return r.status,json.load(r)
        except urllib.error.HTTPError as err:return err.code,json.load(err)

    @classmethod
    def setUpClass(cls):
        for _ in range(30):
            try:
                status,body=cls.request('/login',{'username':os.environ['TEST_ADMIN_EMAIL'],'password':os.environ['TEST_ADMIN_PASSWORD']},form=True)
                if status==200:cls.token=body['access_token'];break
            except (OSError,ValueError):pass
            time.sleep(1)
        else:raise RuntimeError('API de recette indisponible')

    def test_anonymous_cannot_read_financial_campaign_data(self):
        self.assertIn(self.request('/api/v1/campaign-data/quality')[0],[401,403])

    def test_admin_can_read_empty_references_and_invalid_currency_is_refused(self):
        self.assertEqual(self.request('/api/v1/campaign-data/activities',token=self.token)[0],200)
        status,_=self.request('/api/v1/campaign-data/activities',{'code':code(),'name':'Test','currency':'TZS'},self.token)
        self.assertEqual(status,422)

    def test_confirmation_and_report_scope_are_required(self):
        self.assertEqual(self.request('/api/v1/campaign-data/report',token=self.token)[0],422)
        status,_=self.request('/api/v1/campaign-data/campaigns/1/assignments',{'client_operation_id':str(uuid4()),'source_type':'EXPENSE','source_id':1,'source_hash':'a'*64,'reason':'Test'},self.token)
        self.assertEqual(status,422)

    def test_worker_cannot_read_campaign_finances_and_finance_cannot_create_activity(self):
        from app.core.security import Hash
        async def seed(role_name):
            email=code()+'@fixture.invalid'
            async with sessionlocal() as db:
                role=await db.scalar(select(Roles).where(Roles.name==role_name))
                user=Users(first_name='Recette',last_name='Droits',email=email,password_hash=Hash.hash(os.environ['TEST_ADMIN_PASSWORD']),is_active=True)
                db.add(user);await db.flush()
                db.add(UserRole(user_id=user.id,role_id=role.id));await db.commit()
            await engine.dispose()
            return email
        for role_name,read_status in [('Farm Worker',403),('finance_manager',200)]:
            email=asyncio.run(seed(role_name))
            status,body=self.request('/login',{'username':email,'password':os.environ['TEST_ADMIN_PASSWORD']},form=True)
            self.assertEqual(status,200)
            token=body['access_token']
            self.assertEqual(self.request('/api/v1/campaign-data/quality',token=token)[0],read_status)
            self.assertEqual(self.request('/api/v1/campaign-data/activities',{'code':code(),'name':'Interdit'},token)[0],403)
