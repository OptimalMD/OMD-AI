"""add omd_id to user table

Revision ID: b2c3d4e5f6a7
Revises: 1f993805425e
Create Date: 2025-12-06
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "1f993805425e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("user", sa.Column("omd_id", sa.String(), nullable=True))
    # Add unique constraint
    op.create_unique_constraint("uq_user_omd_id", "user", ["omd_id"])

def downgrade() -> None:
    op.drop_constraint("uq_user_omd_id", "user", type_="unique")
    op.drop_column("user", "omd_id")
