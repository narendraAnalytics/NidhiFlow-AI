"""add document type checklist enum values and mismatch columns

Revision ID: c6c1d74b7715
Revises: 473cd15a5e4b
Create Date: 2026-07-23 17:03:21.622450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6c1d74b7715'
down_revision: Union[str, Sequence[str], None] = '473cd15a5e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_DOCUMENT_TYPES = [
    "Form 16",
    "Sale Agreement",
    "Property Valuation Report",
    "Property Tax Receipt",
    "Encumbrance Certificate",
    "Occupancy Certificate",
    "Sale Deed",
    "Employee ID",
    "Udyam Certificate",
    "Shop License",
    "Partnership Deed",
    "MOA",
    "AOA",
    "CIN Certificate",
    "Balance Sheet",
    "Profit & Loss Statement",
    "GST Returns",
    "Audit Report",
]


def upgrade() -> None:
    """Upgrade schema."""
    for value in NEW_DOCUMENT_TYPES:
        op.execute(f"ALTER TYPE document_type ADD VALUE IF NOT EXISTS '{value}'")

    op.add_column(
        'document_validation_results', sa.Column('detected_document_type', sa.String(), nullable=True)
    )
    op.add_column(
        'document_validation_results', sa.Column('type_match_status', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres does not support removing enum values; new DocumentType
    # members are left in place on downgrade (additive-only migration).
    op.drop_column('document_validation_results', 'type_match_status')
    op.drop_column('document_validation_results', 'detected_document_type')
