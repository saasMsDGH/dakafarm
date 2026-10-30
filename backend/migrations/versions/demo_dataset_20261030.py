"""Identifier les simulations et empêcher leur mélange avec les activités réelles."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'demo_dataset_20261030'
down_revision = 'campaign_data_20261030'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('demo_datasets',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('as_of', sa.Date, nullable=False),
        sa.Column('manifest', JSONB, nullable=False),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('activities', sa.Column('demo_dataset', sa.String(50), sa.ForeignKey('demo_datasets.id', ondelete='RESTRICT'), nullable=True))
    op.create_table('demo_sources',
        sa.Column('source_type', sa.String(30), primary_key=True),
        sa.Column('source_id', sa.Integer, primary_key=True),
        sa.Column('dataset_id', sa.String(50), sa.ForeignKey('demo_datasets.id', ondelete='RESTRICT'), nullable=False))
    op.execute('CREATE TRIGGER preserve_demo_sources BEFORE UPDATE OR DELETE ON demo_sources FOR EACH ROW EXECUTE FUNCTION dakafarm_no_mutation()')
    op.execute('CREATE TRIGGER preserve_truncate_demo_sources BEFORE TRUNCATE ON demo_sources FOR EACH STATEMENT EXECUTE FUNCTION dakafarm_no_mutation()')


def downgrade():
    if op.get_bind().execute(sa.text('SELECT EXISTS (SELECT 1 FROM demo_datasets)')).scalar():
        raise RuntimeError('Retour refusé : conserver la provenance des données de démonstration.')
    op.drop_table('demo_sources')
    op.drop_column('activities', 'demo_dataset')
    op.drop_table('demo_datasets')
