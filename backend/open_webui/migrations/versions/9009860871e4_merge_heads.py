"""merge heads

Revision ID: 9009860871e4
Revises: 7b2a1c4d5e6f, d4e5f6a7b8c9
Create Date: 2025-11-28 02:04:20.945047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '9009860871e4'
down_revision: Union[str, None] = ('7b2a1c4d5e6f', 'd4e5f6a7b8c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
