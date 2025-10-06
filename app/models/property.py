# Change user_id to host_id
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, Text, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class PlaceType(str, enum.Enum):
    ENTIRE_PLACE = "entire_place"
    PRIVATE_ROOM = "private_room"
    SHARED_ROOM = "shared_room"

class PropertyType(str, enum.Enum):
    HOUSE = "house"
    APARTMENT  = "apartment"
    GUEST_HOUSE = "guest_house"
    HOTEL = "hotel"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Property(Base):
    __tablename__ = "properties"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    property_type = Column(Enum(PropertyType), nullable=False, index=True)  # house, apartment, etc.
    place_type = Column(Enum(PlaceType), nullable=False, index=True)  # NEW: entire_place, private_room, etc.
    
    # Capacity
    bedrooms = Column(Integer, nullable=False, default=1)
    beds = Column(Integer, nullable=False, default=1)
    bathrooms = Column(Float, nullable=False, default=1.0)
    max_guests = Column(Integer, nullable=False, default=2)
    max_adults = Column(Integer, nullable=False, default=2)
    max_children = Column(Integer, nullable=False, default=0)
    max_infants = Column(Integer, nullable=False, default=0)
    pets_allowed = Column(Boolean, default=False)
    
    # Pricing (in cents to avoid floating point issues)
    price_per_night = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    cleaning_fee = Column(Integer, default=0)
    service_fee = Column(Integer, default=0)
    weekly_discount = Column(Integer, default=0)
    monthly_discount = Column(Integer, default=0)
    
    # Location (Foreign Key)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    verification_status = Column(
        Enum(VerificationStatus), 
        default=VerificationStatus.PENDING,
        nullable=False,
        index=True
    )
    instant_book = Column(Boolean, default=False, index=True)
    
    # Ratings (calculated from reviews)
    average_rating = Column(Float, default=0.0, index=True)
    total_reviews = Column(Integer, default=0)
    
    # Host - DENORMALIZED DATA
    host_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    host_name = Column(String(200), nullable=False)
    host_email = Column(String(255), nullable=False)
    host_avatar = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    location = relationship("Location", back_populates="properties", lazy="joined")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan", lazy="selectin")
    amenities = relationship("Amenity", secondary="property_amenities", back_populates="properties")
    safety_features = relationship("SafetyFeature", secondary="property_safety_features", back_populates="properties")
    availabilities = relationship("Availability", back_populates="property", cascade="all, delete-orphan")
    rules = relationship("PropertyRule", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    experiences = relationship("Experience", secondary="property_experiences", back_populates="properties")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('price_per_night > 0', name='positive_price'),
        CheckConstraint('bedrooms >= 0', name='non_negative_bedrooms'),
        CheckConstraint('beds >= 0', name='non_negative_beds'),
        CheckConstraint('bathrooms >= 0', name='non_negative_bathrooms'),
        CheckConstraint('max_guests > 0', name='positive_max_guests'),
        CheckConstraint('average_rating >= 0 AND average_rating <= 5', name='valid_rating'),
        Index('idx_property_location_active', 'location_id', 'is_active'),
        Index('idx_property_host_active', 'host_id', 'is_active'),
        Index('idx_property_search', 'property_type', 'place_type', 'is_active', 'verification_status'),
    )
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', host='{self.host_name}')>"
    

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Relationships
    properties = relationship("Property", back_populates="location")
    
    __table_args__ = (
        Index('idx_location_coordinates', 'latitude', 'longitude'),
        Index('idx_location_city_country', 'city', 'country'),
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='valid_latitude'),
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='valid_longitude'),
    )
    
    def __repr__(self):
        return f"<Location(city='{self.city}', country='{self.country}')>"
    