"""Axes de campagne, preuves append-only et valorisation explicite. Aucune reprise implicite."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'campaign_data_20261030'
down_revision = '2ac63eddf7a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('activities',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(40), nullable=False, unique=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='XOF'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("currency = 'XOF'", name='ck_activity_currency'))
    op.create_table('campaigns',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('activity_id', sa.Integer, sa.ForeignKey('activities.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('code', sa.String(40), nullable=False, unique=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('start_date', sa.Date, nullable=False), sa.Column('end_date', sa.Date),
        sa.Column('status', sa.String(12), nullable=False, server_default='OPEN'),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('end_date IS NULL OR end_date >= start_date', name='ck_campaign_dates'),
        sa.CheckConstraint("status IN ('OPEN','CLOSED')", name='ck_campaign_status'))
    op.create_table('campaign_events',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('campaign_id', sa.Integer, sa.ForeignKey('campaigns.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('source_type', sa.String(30), nullable=False), sa.Column('source_id', sa.Integer, nullable=False),
        sa.Column('action', sa.String(10), nullable=False),
        sa.Column('previous_event_id', sa.BigInteger, sa.ForeignKey('campaign_events.id', ondelete='RESTRICT'), unique=True),
        sa.Column('client_operation_id', sa.String(36), nullable=False, unique=True),
        sa.Column('payload_hash', sa.String(64), nullable=False), sa.Column('source_hash', sa.String(64), nullable=False),
        sa.Column('snapshot', postgresql.JSONB, nullable=False), sa.Column('reason', sa.Text, nullable=False),
        sa.Column('actor_id', sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("action IN ('ASSIGN','RELEASE')", name='ck_campaign_event_action'),
        sa.CheckConstraint('source_id > 0', name='ck_campaign_event_source_id'))
    op.create_index('ix_campaign_event_source', 'campaign_events', ['source_type','source_id'])
    op.create_index('uq_campaign_event_genesis', 'campaign_events', ['source_type','source_id'], unique=True,
                    postgresql_where=sa.text('previous_event_id IS NULL'))
    op.alter_column('products', 'unit_price', type_=sa.Numeric(20,6), existing_type=sa.Numeric(15,2))
    op.add_column('products', sa.Column('cost_basis', sa.String(24), nullable=False, server_default='UNVERIFIED'))
    op.create_check_constraint('ck_product_cost_basis', 'products', "cost_basis IN ('UNVERIFIED','DECLARED','WEIGHTED_AVERAGE')")
    op.add_column('stock_movements', sa.Column('unit_cost_snapshot', sa.Numeric(20,6)))
    op.add_column('stock_movements', sa.Column('cost_total_fcfa', sa.BigInteger))
    op.add_column('stock_movements', sa.Column('valuation_basis', sa.String(24)))
    op.create_check_constraint('ck_stock_cost_positive', 'stock_movements', 'cost_total_fcfa IS NULL OR cost_total_fcfa >= 0')
    op.create_table('product_valuations',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('quantity', sa.Numeric(20,6), nullable=False), sa.Column('unit_cost', sa.Numeric(20,6), nullable=False),
        sa.Column('basis', sa.String(24), nullable=False), sa.Column('origin', sa.String(20), nullable=False),
        sa.Column('purchase_id', sa.Integer, sa.ForeignKey('purchases.id', ondelete='RESTRICT')),
        sa.Column('client_operation_id', sa.String(36), unique=True), sa.Column('payload_hash', sa.String(64)),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('actor_id', sa.Integer, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('quantity >= 0 AND unit_cost >= 0', name='ck_product_valuation_positive'))
    op.execute("""CREATE FUNCTION dakafarm_no_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'Historique append-only: utiliser une contre-opération' USING ERRCODE='23514'; END $$""")
    for table in ['campaign_events','product_valuations']:
        op.execute(f'CREATE TRIGGER preserve_{table} BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION dakafarm_no_mutation()')
        op.execute(f'CREATE TRIGGER preserve_truncate_{table} BEFORE TRUNCATE ON {table} FOR EACH STATEMENT EXECUTE FUNCTION dakafarm_no_mutation()')
    op.execute("""CREATE FUNCTION dakafarm_campaign_chain() RETURNS trigger LANGUAGE plpgsql AS $$
      DECLARE previous campaign_events%ROWTYPE; terminal campaign_events%ROWTYPE;
      BEGIN
        PERFORM pg_advisory_xact_lock(hashtextextended(NEW.source_type || ':' || NEW.source_id::text, 0));
        SELECT e.* INTO terminal FROM campaign_events e WHERE e.source_type=NEW.source_type AND e.source_id=NEW.source_id
          AND NOT EXISTS (SELECT 1 FROM campaign_events n WHERE n.previous_event_id=e.id);
        IF terminal.id IS DISTINCT FROM NEW.previous_event_id THEN
          RAISE EXCEPTION 'La source a changé de rattachement' USING ERRCODE='23514';
        END IF;
        IF NEW.previous_event_id IS NULL THEN
          IF NEW.action <> 'ASSIGN' THEN RAISE EXCEPTION 'Premier événement invalide' USING ERRCODE='23514'; END IF;
        ELSE
          SELECT * INTO previous FROM campaign_events WHERE id=NEW.previous_event_id;
          IF previous.source_type<>NEW.source_type OR previous.source_id<>NEW.source_id OR previous.action=NEW.action THEN
            RAISE EXCEPTION 'Chaîne de rattachement invalide' USING ERRCODE='23514';
          END IF;
          IF NEW.action='RELEASE' AND previous.campaign_id<>NEW.campaign_id THEN
            RAISE EXCEPTION 'Campagne de correction incohérente' USING ERRCODE='23514';
          END IF;
        END IF;
        RETURN NEW;
      END $$""")
    op.execute('CREATE TRIGGER enforce_campaign_chain BEFORE INSERT ON campaign_events FOR EACH ROW EXECUTE FUNCTION dakafarm_campaign_chain()')


def downgrade():
    # Un retour ne doit pas effacer les preuves, valorisations ou affectations validées.
    connection = op.get_bind()
    if any(connection.execute(sa.text(f'SELECT EXISTS (SELECT 1 FROM {table})')).scalar()
           for table in ['campaign_events','product_valuations','campaigns','activities']):
        raise RuntimeError('Retour refusé : les données de campagne doivent être préservées.')
    op.drop_table('product_valuations')
    op.drop_table('campaign_events')
    op.execute('DROP FUNCTION dakafarm_campaign_chain()')
    op.execute('DROP FUNCTION dakafarm_no_mutation()')
    op.drop_table('campaigns'); op.drop_table('activities')
    op.drop_constraint('ck_stock_cost_positive','stock_movements')
    for name in ['unit_cost_snapshot','cost_total_fcfa','valuation_basis']:op.drop_column('stock_movements',name)
    op.drop_constraint('ck_product_cost_basis','products');op.drop_column('products','cost_basis')
    # Ne pas réduire la précision des prix lors du retour.
