"""add serving fields to recipes

Revision ID: 3f7a2b8c1e0d
Revises: abfaa71b1225
Create Date: 2026-05-23 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f7a2b8c1e0d"
down_revision: Union[str, Sequence[str], None] = "abfaa71b1225"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add serving_unit and serving_weight_g; set servings server default to 1."""
    op.alter_column("recipes", "servings", server_default="1")
    op.add_column(
        "recipes",
        sa.Column(
            "serving_unit",
            sa.String(50),
            nullable=False,
            server_default="portion",
        ),
    )
    op.add_column(
        "recipes",
        sa.Column("serving_weight_g", sa.Numeric(precision=7, scale=2), nullable=True),
    )


def downgrade() -> None:
    """Remove serving_unit and serving_weight_g; clear servings server default."""
    op.drop_column("recipes", "serving_weight_g")
    op.drop_column("recipes", "serving_unit")
    op.alter_column("recipes", "servings", server_default=None)
