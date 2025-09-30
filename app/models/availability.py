from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Availability(Base):
    __tablename__ = "availabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    is_available = Column(Boolean, default=True, nullable=False)
    price_override = Column(Integer, nullable=True)  # Amount in cents, overrides default price
    
    # Relationships
    property = relationship("Property", back_populates="availabilities")
    
    __table_args__ = (
        Index('idx_availability_property_dates', 'property_id', 'start_date', 'end_date'),
        CheckConstraint('end_date >= start_date', name='valid_date_range'),
        CheckConstraint('price_override IS NULL OR price_override > 0', name='positive_price_override'),
    )
    
    def __repr__(self):
        return f"<Availability(property_id={self.property_id}, start={self.start_date}, end={self.end_date})>"