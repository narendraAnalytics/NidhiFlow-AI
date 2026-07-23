"""fix document type enum labels to match member names

Revision ID: e4514c49f53b
Revises: c6c1d74b7715
Create Date: 2026-07-23 18:01:39.031355

The `document_type` Postgres enum has always stored the Python enum's
MEMBER NAMES (e.g. 'PAN_CARD', 'AADHAAR'), not the display .value strings
(e.g. 'PAN Card', 'Aadhaar') -- see the original migration 0d4b63efbaca,
which passed member names to sa.Enum(...). Migration c6c1d74b7715 added
the new loan-type-checklist document types using the .value display
strings instead (e.g. 'Sale Agreement'), which don't match what
SQLAlchemy actually sends on insert (the member name, e.g.
'SALE_AGREEMENT') -- causing "invalid input value for enum document_type"
errors for every new document type. This migration adds the correct
member-name labels. The earlier (unused, harmless) display-string labels
from c6c1d74b7715 are left in place since Postgres cannot drop enum
labels.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4514c49f53b'
down_revision: Union[str, Sequence[str], None] = 'c6c1d74b7715'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_DOCUMENT_TYPE_NAMES = [
    "FORM16",
    "SALE_AGREEMENT",
    "PROPERTY_VALUATION_REPORT",
    "PROPERTY_TAX_RECEIPT",
    "ENCUMBRANCE_CERTIFICATE",
    "OCCUPANCY_CERTIFICATE",
    "SALE_DEED",
    "EMPLOYEE_ID",
    "UDYAM_CERTIFICATE",
    "SHOP_LICENSE",
    "PARTNERSHIP_DEED",
    "MOA",
    "AOA",
    "CIN_CERTIFICATE",
    "BALANCE_SHEET",
    "PROFIT_LOSS_STATEMENT",
    "GST_RETURNS",
    "AUDIT_REPORT",
]


def upgrade() -> None:
    """Upgrade schema."""
    for name in NEW_DOCUMENT_TYPE_NAMES:
        op.execute(f"ALTER TYPE document_type ADD VALUE IF NOT EXISTS '{name}'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres does not support removing enum values.
    pass
