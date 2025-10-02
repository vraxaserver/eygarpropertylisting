"""add host denormalized fields to property

Revision ID: 5c0c956db9d1
Revises: 9463e92a93b4
Create Date: 2025-10-01 13:32:09.422018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c0c956db9d1'
down_revision = '9463e92a93b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('properties', sa.Column('host_name', sa.String(length=200), nullable=True))
    op.add_column('properties', sa.Column('host_email', sa.String(length=255), nullable=True))
    op.add_column('properties', sa.Column('host_avatar', sa.String(length=1000), nullable=True))
    
    # Update existing records with placeholder data
    # You'll need to run a script to populate these from auth service
    op.execute("UPDATE properties SET host_name = 'Host', host_email = '', host_avatar = NULL WHERE host_name IS NULL")
    
    # Make columns non-nullable after populating
    op.alter_column('properties', 'host_name', nullable=False)
    op.alter_column('properties', 'host_email', nullable=False)


def downgrade() -> None:
    op.drop_column('properties', 'host_avatar')
    op.drop_column('properties', 'host_email')
    op.drop_column('properties', 'host_name')
