from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class PropertyImage(Base):
    __tablename__ = "property_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    image_url = Column(String(1000), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_cover = Column(Boolean, default=False)
    alt_text = Column(String(255), nullable=True)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    property = relationship("Property", back_populates="images")
    
    __table_args__ = (
        Index('idx_property_images_order', 'property_id', 'display_order'),
        UniqueConstraint('property_id', 'display_order', name='unique_image_order_per_property'),
    )
    
    def __repr__(self):
        return f"<PropertyImage(id={self.id}, property_id={self.property_id})>"