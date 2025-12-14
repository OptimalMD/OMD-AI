"""add user_type to user table

Revision ID: 7b2a1c4d5e6f
Revises: 3af16a1c9fb6
Create Date: 2025-11-28
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "7b2a1c4d5e6f"
down_revision: Union[str, None] = "3af16a1c9fb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("user", sa.Column("user_type", sa.String(length=20), nullable=True))

def downgrade() -> None:
    op.drop_column("user", "user_type")
