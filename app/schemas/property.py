from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.property import PropertyType, VerificationStatus


class LocationBase(BaseModel):
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class LocationResponse(LocationBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class PropertyImageBase(BaseModel):
    image_url: str = Field(..., max_length=1000)
    display_order: int = Field(default=0, ge=0)
    is_cover: bool = False
    alt_text: Optional[str] = Field(None, max_length=255)


class PropertyImageResponse(PropertyImageBase):
    id: UUID
    property_id: UUID
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50)
    property_type: PropertyType
    bedrooms: int = Field(default=1, ge=0)
    beds: int = Field(default=1, ge=0)
    bathrooms: float = Field(default=1.0, ge=0)
    max_guests: int = Field(default=2, gt=0)
    max_adults: int = Field(default=2, ge=0)
    max_children: int = Field(default=0, ge=0)
    max_infants: int = Field(default=0, ge=0)
    pets_allowed: bool = False
    price_per_night: int = Field(..., gt=0)  # In cents
    currency: str = Field(default="USD", min_length=3, max_length=3)
    cleaning_fee: int = Field(default=0, ge=0)
    service_fee: int = Field(default=0, ge=0)
    weekly_discount: int = Field(default=0, ge=0, le=100)  # Percentage
    monthly_discount: int = Field(default=0, ge=0, le=100)  # Percentage
    instant_book: bool = False


class PropertyCreate(PropertyBase):
    location: LocationBase
    amenity_ids: List[UUID] = Field(default_factory=list)
    safety_feature_ids: List[UUID] = Field(default_factory=list)
    images: List[PropertyImageBase] = Field(..., min_length=3)
    house_rules: List[str] = Field(default_factory=list)
    cancellation_policy: Optional[str] = None
    check_in_policy: Optional[str] = None
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if len(v) < 3:
            raise ValueError('Property must have at least 3 images')
        cover_images = [img for img in v if img.is_cover]
        if len(cover_images) == 0:
            v[0].is_cover = True
        elif len(cover_images) > 1:
            raise ValueError('Only one image can be marked as cover')
        return v


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=50)
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0)
    beds: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    max_guests: Optional[int] = Field(None, gt=0)
    max_adults: Optional[int] = Field(None, ge=0)
    max_children: Optional[int] = Field(None, ge=0)
    max_infants: Optional[int] = Field(None, ge=0)
    pets_allowed: Optional[bool] = None
    price_per_night: Optional[int] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    cleaning_fee: Optional[int] = Field(None, ge=0)
    service_fee: Optional[int] = Field(None, ge=0)
    weekly_discount: Optional[int] = Field(None, ge=0, le=100)
    monthly_discount: Optional[int] = Field(None, ge=0, le=100)
    instant_book: Optional[bool] = None
    is_active: Optional[bool] = None
    location: Optional[LocationBase] = None
    amenity_ids: Optional[List[UUID]] = None
    safety_feature_ids: Optional[List[UUID]] = None


class PropertyResponse(PropertyBase):
    id: UUID
    slug: str
    user_id: UUID
    location: LocationResponse
    is_active: bool
    is_featured: bool
    verification_status: VerificationStatus
    average_rating: float
    total_reviews: int
    images: List[PropertyImageResponse]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class PropertyListResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    property_type: PropertyType
    price_per_night: int
    currency: str
    bedrooms: int
    beds: int
    bathrooms: float
    max_guests: int
    average_rating: float
    total_reviews: int
    is_featured: bool
    location: LocationResponse
    cover_image: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)