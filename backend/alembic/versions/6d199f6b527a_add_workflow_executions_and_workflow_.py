"""add workflow_executions and workflow_events tables

Revision ID: 6d199f6b527a
Revises: 00cc34902232
Create Date: 2026-07-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6d199f6b527a'
down_revision: Union[str, Sequence[str], None] = '00cc34902232'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('workflow_executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('loan_application_id', sa.UUID(), nullable=False),
    sa.Column('workflow_status', sa.String(), nullable=False),
    sa.Column('current_stage', sa.String(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration', sa.Float(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['loan_application_id'], ['loan_applications.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_executions_loan_application_id'), 'workflow_executions', ['loan_application_id'], unique=False)
    op.create_table('workflow_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workflow_execution_id', sa.UUID(), nullable=False),
    sa.Column('stage', sa.String(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['workflow_execution_id'], ['workflow_executions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_events_workflow_execution_id'), 'workflow_events', ['workflow_execution_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_workflow_events_workflow_execution_id'), table_name='workflow_events')
    op.drop_table('workflow_events')
    op.drop_index(op.f('ix_workflow_executions_loan_application_id'), table_name='workflow_executions')
    op.drop_table('workflow_executions')
