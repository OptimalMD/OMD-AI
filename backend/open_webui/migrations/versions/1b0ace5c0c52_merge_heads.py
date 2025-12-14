"""merge heads

Revision ID: 1b0ace5c0c52
Revises: 9009860871e4, f2a3b4c5d6e7
Create Date: 2025-12-05 09:52:05.736425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '1b0ace5c0c52'
down_revision: Union[str, None] = ('9009860871e4', 'f2a3b4c5d6e7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
