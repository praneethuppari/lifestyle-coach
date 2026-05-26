"""require hashed_password on users

Revision ID: 93a7519a1526
Revises: b349a832bf15
Create Date: 2026-05-25 16:30:46.119581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93a7519a1526'
down_revision: Union[str, Sequence[str], None] = 'b349a832bf15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove any users created before auth was required (no password set).
    op.execute("DELETE FROM users WHERE hashed_password IS NULL")
    op.alter_column("users", "hashed_password", nullable=False)


def downgrade() -> None:
    op.alter_column("users", "hashed_password", nullable=True)
