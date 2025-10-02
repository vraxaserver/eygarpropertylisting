"""rename user_id to host_id

Revision ID: 9463e92a93b4
Revises: c4eace5a4ecd
Create Date: 2025-10-01 10:15:04.442902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9463e92a93b4'
down_revision = 'c4eace5a4ecd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename column
    op.alter_column('properties', 'user_id', new_column_name='host_id')
    
    # Rename index
    op.drop_index('idx_property_user_active', table_name='properties')
    op.create_index('idx_property_host_active', 'properties', ['host_id', 'is_active'])


def downgrade() -> None:
    # Revert column rename
    op.alter_column('properties', 'host_id', new_column_name='user_id')
    
    # Revert index rename
    op.drop_index('idx_property_host_active', table_name='properties')
    op.create_index('idx_property_user_active', 'properties', ['user_id', 'is_active'])
