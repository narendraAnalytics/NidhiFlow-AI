"""add node_executions table

Revision ID: 9a3e2f7c1d4b
Revises: 6d199f6b527a
Create Date: 2026-07-22 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9a3e2f7c1d4b'
down_revision: Union[str, Sequence[str], None] = '6d199f6b527a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('node_executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workflow_execution_id', sa.UUID(), nullable=False),
    sa.Column('node_name', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration', sa.Float(), nullable=True),
    sa.Column('error_category', sa.String(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_attempt', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['workflow_execution_id'], ['workflow_executions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_node_executions_workflow_execution_id'), 'node_executions', ['workflow_execution_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_node_executions_workflow_execution_id'), table_name='node_executions')
    op.drop_table('node_executions')
