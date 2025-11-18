"""Add organization table

Revision ID: c2d3e4f5a6b7
Revises: b1f2e3d4c5a6
Create Date: 2025-11-18 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, None] = "b1f2e3d4c5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organization table
    op.create_table(
        "organization",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("org_name", sa.Text(), nullable=False),
        sa.Column("org_code", sa.Text(), nullable=False),
        sa.Column("plans", sa.JSON(), nullable=True),
        sa.Column("users", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("signup_enabled", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("org_code"),
    )

    # Create indexes for better performance
    op.create_index("idx_organization_org_code", "organization", ["org_code"], unique=True)
    op.create_index("idx_organization_status", "organization", ["status"])
    op.create_index("idx_organization_signup_enabled", "organization", ["signup_enabled"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("idx_organization_signup_enabled", table_name="organization")
    op.drop_index("idx_organization_status", table_name="organization")
    op.drop_index("idx_organization_org_code", table_name="organization")

    # Drop the table
    op.drop_table("organization")
