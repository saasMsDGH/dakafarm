"""Scénario avicole : flux physiques, paies, coûts et retour de trésorerie rapprochés."""
from decimal import Decimal
import unittest
from sqlalchemy import select, func, text
import app.db
from app.core.database import engine,sessionlocal
from app.api.v1.user.models import Users
from app.api.v1.campaigns.models import DemoDataset,CampaignEvent
from app.api.v1.campaigns.poultry_models import PoultryCampaign,PayrollAllocation,RetiredDemoSource
from app.api.v1.campaigns.service import report
from app.api.v1.hr.models.payroll import Payroll
from app.api.v1.inventory.models.product import Product
from app.api.v1.farm.models.flock import Flock
from app.api.v1.farm.models.production_record import ProductionRecord
from app.demo_seed import seed_demo,AS_OF,DATASET
from app.poultry_seed import seed_poultry,allocate,EXTENSION

class PoultryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db=sessionlocal();self.actor=await self.db.scalar(select(Users.id).order_by(Users.id).limit(1))

    async def asyncTearDown(self):
        await self.db.close();await engine.dispose()

    async def test_a_poultry_cycle_and_payroll_reconcile(self):
        await seed_demo(self.db,self.actor,if_absent=True);await self.db.commit()
        result=await seed_poultry(self.db,self.actor);await self.db.commit()
        self.assertFalse(result['replayed'])
        data=await report(self.db,result['campaign_ids'],AS_OF)
        self.assertEqual(data['quality']['issues'],[])
        self.assertTrue(data['quality']['result_available'])
        self.assertEqual(len(data['poultry']['campaigns']),4)
        self.assertEqual(data['poultry']['employee_count'],10)
        self.assertEqual(data['poultry']['customer_count'],10)
        self.assertEqual(data['poultry']['salary_mean_fcfa'],'100000')
        pays=list((await self.db.scalars(select(Payroll).where(Payroll.employee_id.in_(result['employee_ids'])))).all())
        self.assertEqual(len(pays),340)
        self.assertEqual(sum(p.net_salary for p in pays),Decimal('34000000'))
        self.assertTrue(all(p.basic_salary==100000 for p in pays))
        self.assertEqual(sum(int(c['wages']) for c in data['poultry']['campaigns']),34000000)
        self.assertEqual(sum(int(c['eggs_produced']) for c in data['poultry']['campaigns']),sum(int(c['eggs_sold']) for c in data['poultry']['campaigns']))
        self.assertEqual(sum(int(c['hens_sold'])>0 for c in data['poultry']['campaigns']),2)
        for c in data['poultry']['campaigns']:
            self.assertEqual(int(c['birds_bought'])-int(c['deaths'])-int(c['hens_sold']),int(c['birds_remaining']))
            self.assertGreater(int(c['egg_revenue']),0)
            self.assertGreater(int(c['feed_cost']),0)
            self.assertGreater(int(c['vaccine_cost']),0)
            self.assertIsNotNone(c['cash_roi_percent'])
            self.assertGreater(int(c['capital_fcfa']),0)
        self.assertEqual(await self.db.scalar(select(func.count()).select_from(Product).where(Product.current_stock<0)),0)
        snapshots=(await self.db.scalars(select(ProductionRecord).where(ProductionRecord.bird_days.is_not(None)))).all()
        self.assertTrue(all(r.period_start_date<=r.record_date and r.laying_percentage<=100 for r in snapshots))
        before=await self.db.scalar(select(func.count()).select_from(CampaignEvent))
        again=await seed_poultry(self.db,self.actor,if_absent=True);await self.db.commit()
        self.assertTrue(again['replayed'])
        self.assertEqual(before,await self.db.scalar(select(func.count()).select_from(CampaignEvent)))
        self.assertGreater(await self.db.scalar(select(func.count()).select_from(RetiredDemoSource)),0)

    async def test_b_rounding_never_duplicates_or_loses_salary(self):
        for weights in [{1:1000,2:1200,3:1400},{1:1,2:1,3:1},{1:1}]:
            amounts=allocate(100000,weights)
            self.assertEqual(sum(amounts.values()),100000)
            self.assertTrue(all(v>0 for v in amounts.values()))

    async def test_c_mid_period_report_does_not_include_future_eggs_or_wages(self):
        marker=await self.db.get(DemoDataset,EXTENSION)
        self.assertIsNotNone(marker)
        from datetime import date
        early=await report(self.db,marker.manifest['campaign_ids'],date(2024,1,1))
        self.assertEqual(early['totals']['revenue'],'0')
        self.assertEqual(early['totals']['eggs'],'0')
        self.assertEqual(early['totals']['expense'],'0')
        self.assertTrue(all(c['wages']=='0' for c in early['poultry']['campaigns']))

    async def test_d_payroll_drift_blocks_roi(self):
        marker=await self.db.get(DemoDataset,EXTENSION);ids=marker.manifest['campaign_ids']
        pid=await self.db.scalar(select(Payroll.id).where(Payroll.employee_id.in_(marker.manifest['employee_ids'])).limit(1))
        await self.db.execute(text('UPDATE payrolls SET net_salary=100001 WHERE id=:id'),{'id':pid});await self.db.commit()
        try:
            data=await report(self.db,ids,AS_OF)
            self.assertFalse(data['quality']['result_available'])
            self.assertIsNone(data['poultry']['cash_roi_percent'])
            self.assertIn('PAYROLL_RECONCILIATION_REQUIRED',[i['type'] for i in data['quality']['issues']])
        finally:
            await self.db.execute(text('UPDATE payrolls SET net_salary=100000 WHERE id=:id'),{'id':pid});await self.db.commit()
