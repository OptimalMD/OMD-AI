"""Add user organization field

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2025-12-05 00:00:02.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add organization_id column to user table
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("organization_id", sa.String(), nullable=True))


def downgrade() -> None:
    # Remove organization_id column from user table
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("organization_id")
