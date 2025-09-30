from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Index, CheckConstraint, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to auth service
    
    # Overall rating
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    
    # Detailed ratings
    cleanliness_rating = Column(Integer, nullable=True)  # 1-5
    accuracy_rating = Column(Integer, nullable=True)  # 1-5
    communication_rating = Column(Integer, nullable=True)  # 1-5
    location_rating = Column(Integer, nullable=True)  # 1-5
    check_in_rating = Column(Integer, nullable=True)  # 1-5
    value_rating = Column(Integer, nullable=True)  # 1-5
    
    # Metadata
    helpful_count = Column(Integer, default=0, nullable=False)
    reported = Column(Boolean, default=False, nullable=False)
    is_verified_stay = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    property = relationship("Property", back_populates="reviews")
    
    __table_args__ = (
        UniqueConstraint('property_id', 'user_id', name='one_review_per_user_per_property'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_overall_rating'),
        CheckConstraint('cleanliness_rating IS NULL OR (cleanliness_rating >= 1 AND cleanliness_rating <= 5)', name='valid_cleanliness'),
        CheckConstraint('accuracy_rating IS NULL OR (accuracy_rating >= 1 AND accuracy_rating <= 5)', name='valid_accuracy'),
        CheckConstraint('communication_rating IS NULL OR (communication_rating >= 1 AND communication_rating <= 5)', name='valid_communication'),
        CheckConstraint('location_rating IS NULL OR (location_rating >= 1 AND location_rating <= 5)', name='valid_location'),
        CheckConstraint('check_in_rating IS NULL OR (check_in_rating >= 1 AND check_in_rating <= 5)', name='valid_check_in'),
        CheckConstraint('value_rating IS NULL OR (value_rating >= 1 AND value_rating <= 5)', name='valid_value'),
        CheckConstraint('helpful_count >= 0', name='non_negative_helpful'),
        Index('idx_review_property_created', 'property_id', 'created_at'),
        Index('idx_review_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, property_id={self.property_id}, rating={self.rating})>"