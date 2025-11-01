"""Added vendors services model

Revision ID: da569ab6c9ac
Revises: 4aaaf2ede99b
Create Date: 2025-10-30 12:33:37.414295

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'da569ab6c9ac'
down_revision = '4aaaf2ede99b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('vendor_services',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('vendorId', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('vendorName', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('allowedGuests', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('image', sa.String(), nullable=False),
    sa.Column('isActive', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('serviceArea', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('rating', sa.Float(), server_default=sa.text('0'), nullable=False),
    sa.Column('reviewCount', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vendor_services_vendorId'), 'vendor_services', ['vendorId'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_vendor_services_vendorId'), table_name='vendor_services')
    op.drop_table('vendor_services')
    # ### end Alembic commands ###
