"""add hashed_password to users

Revision ID: c3e9a14f82b1
Revises: abfaa71b1225
Create Date: 2026-05-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3e9a14f82b1"
down_revision: str | None = "abfaa71b1225"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
