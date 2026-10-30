"""Simulation multi-activité : chiffres réconciliés, rejeu et séparation du réel."""
from collections import Counter
from datetime import date
from decimal import Decimal
import unittest
from unittest.mock import patch
from sqlalchemy import select, func, text
from fastapi import HTTPException
import app.db
from app.core.database import engine, sessionlocal
from app.api.v1.campaigns.models import Activity, Campaign, CampaignEvent, DemoDataset, DemoSource
from app.api.v1.campaigns import service
from app.api.v1.campaigns.schemas import ActivityCreate, CampaignCreate, AssignmentCreate
from app.api.v1.campaigns.sources import SOURCES, measures, project, fingerprint
from app.api.v1.pos.models.expense import Expense
from uuid import uuid4
from datetime import datetime, timezone
from app.api.v1.inventory.models.stock_movement import StockMovement
from app.api.v1.inventory.models.product import Product
from app.api.v1.user.models import Users
from app.demo_seed import seed_demo, DATASET, AS_OF, SCENARIOS

class DemoDatasetTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db=sessionlocal()
        self.actor=await self.db.scalar(select(Users.id).order_by(Users.id).limit(1))

    async def asyncTearDown(self):
        await self.db.close()
        await engine.dispose()

    async def counts(self):
        return {kind:await self.db.scalar(select(func.count()).select_from(model)) for kind,(model,_,_) in SOURCES.items()}

    async def test_a_import_is_atomic_on_intermediate_failure(self):
        before=await self.counts()
        from app.api.v1.campaigns.sources import project
        calls=0
        def fail(kind,row):
            nonlocal calls
            calls+=1
            if calls==12:raise RuntimeError('Panne simulée pendant import')
            return project(kind,row)
        with patch('app.demo_seed.project',side_effect=fail):
            with self.assertRaises(RuntimeError):await seed_demo(self.db,self.actor)
        await self.db.rollback()
        self.assertEqual(before,await self.counts())
        self.assertIsNone(await self.db.get(DemoDataset,DATASET))
        self.assertEqual(await self.db.scalar(select(func.count()).select_from(DemoSource)),0)

    async def test_b_eight_activities_four_campaigns_balanced_and_replay_safe(self):
        manifest=await seed_demo(self.db,self.actor);await self.db.commit()
        self.assertFalse(manifest['replayed'])
        self.assertEqual(len(manifest['campaign_ids']),32)
        report=await service.report(self.db,manifest['campaign_ids'],AS_OF)
        self.assertTrue(report['quality']['result_available'])
        self.assertEqual(report['quality']['issues'],[])
        self.assertTrue(all(a['campaign_count']==4 for a in report['by_activity']))
        self.assertEqual({a['name'] for a in report['by_activity']},{s[1] for s in SCENARIOS})
        self.assertEqual(sum(int(a['result_fcfa']) for a in report['by_activity']),int(report['totals']['result_fcfa']))
        self.assertEqual(sum(int(a['cash_net_fcfa']) for a in report['by_activity']),int(report['totals']['cash_net_fcfa']))
        self.assertTrue(any(int(a['result_fcfa'])<0 for a in report['by_activity']))
        self.assertTrue(any(int(a['result_fcfa'])>0 and int(a['cash_net_fcfa'])<0 for a in report['by_activity']))
        self.assertTrue(any(a['status']=='Excédentaire' for a in report['by_activity']))
        self.assertEqual(len(report['activity_monthly']),34)
        for activity in report['by_activity']:
            self.assertEqual(report['activity_monthly'][-1][f"activity_{activity['activity_id']}"],activity['cash_before_funding_fcfa'])
            self.assertGreaterEqual(int(activity['funding_gap_fcfa']),0)
        before=await self.counts()
        replay=await seed_demo(self.db,self.actor);await self.db.commit()
        self.assertTrue(replay['replayed']);self.assertEqual(before,await self.counts())
        once=await seed_demo(self.db,self.actor,if_absent=True);await self.db.commit()
        self.assertTrue(once['replayed']);self.assertEqual(before,await self.counts())
        # Le solde courant de chaque produit est exactement la somme de ses entrées/sorties.
        products=(await self.db.scalars(select(Product).where(Product.name.like('[DÉMO]%')))).all()
        for product in products:
            rows=(await self.db.scalars(select(StockMovement).where(StockMovement.product_id==product.id))).all()
            balance=sum((r.quantity if r.movement_type=='IN' else -r.quantity for r in rows),Decimal(0))
            self.assertEqual(product.current_stock,balance)
            self.assertGreaterEqual(balance,0)

    async def test_c_demo_and_real_cannot_be_consolidated(self):
        dataset=await self.db.get(DemoDataset,DATASET)
        self.assertIsNotNone(dataset)
        demo_campaign_id=dataset.manifest['campaign_ids'][0]
        activity=await service.create_activity(self.db,ActivityCreate(code='REAL-SCOPE-TEST',name='Activité réelle indépendante'),self.actor)
        campaign=await service.create_campaign(self.db,CampaignCreate(activity_id=activity['id'],code='REAL-SCOPE-C1',name='Campagne indépendante',start_date=date(2026,1,1)),self.actor)
        with self.assertRaises(HTTPException) as error:
            await service.report(self.db,[campaign['id'],demo_campaign_id],AS_OF)
        self.assertEqual(error.exception.status_code,422)
        # Une pièce réelle ne doit pas pouvoir se glisser dans une campagne fictive.
        expense=Expense(expense_number='REAL-PROVENANCE-TEST',category='Réel',amount=Decimal('1000'),expense_date=datetime(2025,1,1,tzinfo=timezone.utc))
        self.db.add(expense);await self.db.commit();await self.db.refresh(expense)
        request=AssignmentCreate(client_operation_id=uuid4(),source_type='EXPENSE',source_id=expense.id,
            source_hash=fingerprint(project('EXPENSE',expense)),confirm_currency='XOF',reason='Essai de mélange à refuser')
        with self.assertRaises(HTTPException) as error:
            await service.assign(self.db,demo_campaign_id,request,self.actor)
        self.assertEqual(error.exception.status_code,409)
        self.assertIn('démonstration',error.exception.detail)

    async def test_d_daily_funding_gap_prevents_month_end_netting(self):
        dataset=await self.db.get(DemoDataset,DATASET)
        report=await service.report(self.db,dataset.manifest['campaign_ids'],AS_OF)
        early=await service.report(self.db,dataset.manifest['campaign_ids'],date(2024,1,1))
        # Les apports initiaux sont séparés des recettes et le décaissement du lot entier
        # reste visible, même si les ventes de fin de mois réduisent le besoin.
        self.assertEqual(early['totals']['revenue'],'0')
        self.assertGreater(int(early['totals']['funding_in']),0)
        self.assertTrue(all(int(a['funding_gap_fcfa'])>=int(a['cash_out']) for a in early['by_activity']))
        self.assertEqual(report['demo_dataset'],DATASET)
