"""add user phone and subscription fields

Revision ID: d4e5f6a7b8c9
Revises: c2d3e4f5a6b7
Create Date: 2025-11-18 00:00:02.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add phone column
    op.add_column("user", sa.Column("phone", sa.String(length=20), nullable=True))
    
    # Add subscription fields
    op.add_column("user", sa.Column("subscription_id", sa.String(), nullable=True))
    op.add_column("user", sa.Column("subscription_status", sa.String(), nullable=True))


def downgrade() -> None:
    # Remove subscription fields
    op.drop_column("user", "subscription_status")
    op.drop_column("user", "subscription_id")
    
    # Remove phone column
    op.drop_column("user", "phone")
