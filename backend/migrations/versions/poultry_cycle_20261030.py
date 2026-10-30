"""Campagnes de ponte, paies ventilées et historique de simulation préservé."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
revision='poultry_cycle_20261030'
down_revision='demo_dataset_20261030'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('production_records',sa.Column('period_start_date',sa.Date,nullable=True))
    op.add_column('production_records',sa.Column('bird_days',sa.Integer,nullable=True))
    op.create_check_constraint('ck_production_period','production_records',
        '(period_start_date IS NULL AND bird_days IS NULL) OR (period_start_date IS NOT NULL AND bird_days > 0 AND period_start_date <= record_date)')
    op.create_table('poultry_campaigns',
        sa.Column('campaign_id',sa.Integer,sa.ForeignKey('campaigns.id',ondelete='RESTRICT'),primary_key=True),
        sa.Column('flock_id',sa.Integer,sa.ForeignKey('flocks.id',ondelete='RESTRICT'),nullable=False,unique=True),
        *[sa.Column(name,sa.Integer,sa.ForeignKey('products.id',ondelete='RESTRICT'),nullable=False) for name in ['bird_product_id','egg_product_id','feed_product_id','vaccine_product_id']],
        sa.Column('assumptions',JSONB,nullable=False))
    op.create_table('payroll_allocations',
        sa.Column('id',sa.BigInteger,primary_key=True,autoincrement=True),
        sa.Column('payroll_id',sa.Integer,sa.ForeignKey('payrolls.id',ondelete='RESTRICT'),nullable=False,index=True),
        sa.Column('campaign_id',sa.Integer,sa.ForeignKey('campaigns.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('employee_id',sa.Integer,sa.ForeignKey('employees.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('allocation_date',sa.Date,nullable=False),
        sa.Column('amount_fcfa',sa.BigInteger,nullable=False),sa.Column('payroll_net_fcfa',sa.BigInteger,nullable=False),
        sa.Column('pay_period',sa.String(50),nullable=False),sa.Column('method',sa.Text,nullable=False),
        sa.Column('created_by',sa.Integer,sa.ForeignKey('users.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.UniqueConstraint('payroll_id','campaign_id',name='uq_payroll_campaign'),
        sa.CheckConstraint('amount_fcfa >= 0 AND payroll_net_fcfa >= amount_fcfa',name='ck_payroll_allocation_amount'))
    op.create_table('retired_demo_sources',
        sa.Column('source_type',sa.String(30),primary_key=True),sa.Column('source_id',sa.Integer,primary_key=True),
        sa.Column('extension_id',sa.String(50),sa.ForeignKey('demo_datasets.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('reason',sa.Text,nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False))
    for table in ['poultry_campaigns','payroll_allocations','retired_demo_sources']:
        op.execute(f'CREATE TRIGGER preserve_{table} BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION dakafarm_no_mutation()')
        op.execute(f'CREATE TRIGGER preserve_truncate_{table} BEFORE TRUNCATE ON {table} FOR EACH STATEMENT EXECUTE FUNCTION dakafarm_no_mutation()')


def downgrade():
    for table in ['poultry_campaigns','payroll_allocations','retired_demo_sources']:
        if op.get_bind().execute(sa.text(f'SELECT EXISTS (SELECT 1 FROM {table})')).scalar():
            raise RuntimeError('Retour refusé : conserver les données avicoles et salariales.')
    for table in ['retired_demo_sources','payroll_allocations','poultry_campaigns']:op.drop_table(table)
    op.drop_constraint('ck_production_period','production_records')
    op.drop_column('production_records','bird_days');op.drop_column('production_records','period_start_date')
