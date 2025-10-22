"""Add Property and PropertyPhoto tables and update BrochureDraft

Revision ID: ae5d1c000110  
Revises: ae5d1c000109
Create Date: 2025-10-19 14:20:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ae5d1c000110"
down_revision = "ae5d1c000109" 
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create properties table
    op.create_table(
        'properties',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('building', sa.String(255), nullable=False, index=True),
        sa.Column('community', sa.String(255), nullable=True, index=True),
        sa.Column('unit', sa.String(100), nullable=True),
        sa.Column('property_type', sa.Enum('apartment', 'villa', 'townhouse', 'mixed', name='propertytype'), 
                 server_default='apartment', nullable=False),
        sa.Column('beds', sa.Integer(), nullable=True),
        sa.Column('baths', sa.Float(), nullable=True),
        sa.Column('area_sqft', sa.Float(), nullable=True),
        sa.Column('price_aed', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_lat', sa.Float(), nullable=True),
        sa.Column('location_lng', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'archived', name='propertystatus'), 
                 server_default='draft', nullable=False, index=True)
    )
    
    # Create property_photos table
    op.create_table(
        'property_photos',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('property_id', sa.String(36), nullable=False, index=True),
        sa.Column('url', sa.String(512), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE')
    )
    
    # Add property_id to brochure_drafts table
    op.add_column('brochure_drafts', sa.Column('property_id', sa.String(36), nullable=True, index=True))
    op.create_foreign_key('fk_brochure_drafts_property_id', 'brochure_drafts', 'properties', ['property_id'], ['id'])
    
    # Create indexes
    op.create_index('idx_property_building_unit', 'properties', ['building', 'unit'])
    op.create_index('idx_property_status', 'properties', ['status'])
    op.create_index('idx_photo_property_sort', 'property_photos', ['property_id', 'sort_order'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_photo_property_sort', table_name='property_photos')
    op.drop_index('idx_property_status', table_name='properties')  
    op.drop_index('idx_property_building_unit', table_name='properties')
    
    # Remove property_id from brochure_drafts
    op.drop_constraint('fk_brochure_drafts_property_id', 'brochure_drafts', type_='foreignkey')
    op.drop_column('brochure_drafts', 'property_id')
    
    # Drop tables
    op.drop_table('property_photos')
    op.drop_table('properties')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS propertystatus')
    op.execute('DROP TYPE IF EXISTS propertytype')