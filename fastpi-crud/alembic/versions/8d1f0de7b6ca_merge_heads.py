"""merge heads

Revision ID: 8d1f0de7b6ca
Revises: abc123, dadd56e0c400
Create Date: 2026-04-23 12:39:31.456482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d1f0de7b6ca'
down_revision: Union[str, Sequence[str], None] = ('abc123', 'dadd56e0c400')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
