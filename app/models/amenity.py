from sqlalchemy import Column, String, Enum, ForeignKey, Table, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class AmenityCategory(str, enum.Enum):
    BASIC = "basic"
    SAFETY = "safety"
    ACCESSIBILITY = "accessibility"
    KITCHEN = "kitchen"
    ENTERTAINMENT = "entertainment"


# Association table for Property-Amenity many-to-many relationship
property_amenities = Table(
    'property_amenities',
    Base.metadata,
    Column('property_id', UUID(as_uuid=True), ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    Column('amenity_id', UUID(as_uuid=True), ForeignKey('amenities.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_property_amenities_property', 'property_id'),
    Index('idx_property_amenities_amenity', 'amenity_id'),
)


class Amenity(Base):
    __tablename__ = "amenities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(Enum(AmenityCategory), nullable=False, index=True)
    icon = Column(String(50), nullable=True)  # Icon name or emoji
    
    # Relationships
    properties = relationship("Property", secondary=property_amenities, back_populates="amenities")
    
    def __repr__(self):
        return f"<Amenity(name='{self.name}', category='{self.category}')>"


# Association table for Property-SafetyFeature many-to-many relationship
property_safety_features = Table(
    'property_safety_features',
    Base.metadata,
    Column('property_id', UUID(as_uuid=True), ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    Column('safety_feature_id', UUID(as_uuid=True), ForeignKey('safety_features.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_property_safety_features_property', 'property_id'),
    Index('idx_property_safety_features_feature', 'safety_feature_id'),
)


class SafetyFeature(Base):
    __tablename__ = "safety_features"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    icon = Column(String(50), nullable=True)
    
    # Relationships
    properties = relationship("Property", secondary=property_safety_features, back_populates="safety_features")
    
    def __repr__(self):
        return f"<SafetyFeature(name='{self.name}')>"