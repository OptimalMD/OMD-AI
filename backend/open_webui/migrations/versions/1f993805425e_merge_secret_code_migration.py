"""merge secret_code migration

Revision ID: 1f993805425e
Revises: 1b0ace5c0c52, a1b2c3d4e5f6
Create Date: 2025-12-06 19:16:20.125160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '1f993805425e'
down_revision: Union[str, None] = ('1b0ace5c0c52', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
