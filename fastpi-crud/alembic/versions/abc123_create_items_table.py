# alembic/versions/abc123_create_items_table.py
"""create items table

Revision ID: abc123
Revises: 
Create Date: 2024-01-15 10:30:00

"""
from alembic import op
import sqlalchemy as sa

# The revision ID of THIS migration
revision = 'abc123'
# The revision this one builds on (None = first migration)
down_revision = None
depends_on = None


def upgrade() -> None:
    """Apply this migration (move forward)."""
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)


def downgrade() -> None:
    """Undo this migration (move backward)."""
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')