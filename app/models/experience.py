from sqlalchemy import Column, String, Text, ForeignKey, Table, Index, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid
from app.database import Base


# Association table for Property-Experience many-to-many relationship
property_experiences = Table(
    'property_experiences',
    Base.metadata,
    Column('property_id', UUID(as_uuid=True), ForeignKey('properties.id', ondelete='CASCADE'), primary_key=True),
    Column('experience_id', UUID(as_uuid=True), ForeignKey('experiences.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_property_experiences_property', 'property_id'),
    Index('idx_property_experiences_experience', 'experience_id'),
)


class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=False)
    
    # Host who created this experience
    host_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Eligibility conditions
    min_nights = Column(Integer, default=1)  # Minimum nights stay required
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    properties = relationship(
        "Property",
        secondary=property_experiences,
        back_populates="experiences"
    )
    
    __table_args__ = (
        Index('idx_experience_host_active', 'host_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Experience(id={self.id}, title='{self.title}')>"