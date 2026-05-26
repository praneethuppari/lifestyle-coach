"""merge serving fields and hashed password

Revision ID: b349a832bf15
Revises: 3f7a2b8c1e0d, c3e9a14f82b1
Create Date: 2026-05-25 16:22:13.205646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b349a832bf15'
down_revision: Union[str, Sequence[str], None] = ('3f7a2b8c1e0d', 'c3e9a14f82b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
