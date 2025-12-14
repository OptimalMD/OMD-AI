"""Add organization logos

Revision ID: e1f2a3b4c5d6
Revises: c2d3e4f5a6b7
Create Date: 2025-12-05 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add dark_logo and light_logo columns to organization table
    with op.batch_alter_table("organization", schema=None) as batch_op:
        batch_op.add_column(sa.Column("dark_logo", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("light_logo", sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove dark_logo and light_logo columns from organization table
    with op.batch_alter_table("organization", schema=None) as batch_op:
        batch_op.drop_column("light_logo")
        batch_op.drop_column("dark_logo")
