# app/schemas/vendor_service.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

# Using an Enum for category ensures data consistency
class ServiceCategory(str, Enum):
    FOOD = "Food"
    COACHING = "Coaching"
    TRAINING = "Training"
    CAR_RENTAL = "Car rental"
    LOCAL_GUIDE = "Local Guide"
    CLUBBING = "Clubbing"
    WORKSHOP = "Workshop"
    OTHER = "Other"

# Schema for the Service Area JSON object
class ServiceAreaSchema(BaseModel):
    name: str
    lat: float
    lng: float
    radius: int

# Base schema with common fields
class VendorServiceBase(BaseModel):
    title: str = Field(..., example="Professional Dance Class")
    description: str = Field(..., example="A fun and energetic dance class for all levels.")
    category: ServiceCategory = Field(..., example=ServiceCategory.TRAINING)
    duration: int = Field(..., example=2, description="Duration in hours")
    allowedGuests: int = Field(..., example=10)
    price: float = Field(..., example=100.0)
    serviceArea: ServiceAreaSchema
    image: str = Field(..., example="https://example.com/image.jpg")
    isActive: bool = True

# Schema for creating a new service (input)
# vendorId and vendorName will be taken from the logged-in user
class VendorServiceCreate(VendorServiceBase):
    pass

# Schema for updating a service (input)
# All fields are optional
class VendorServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ServiceCategory] = None
    duration: Optional[int] = None
    allowedGuests: Optional[int] = None
    price: Optional[float] = None
    serviceArea: Optional[ServiceAreaSchema] = None
    image: Optional[str] = None
    isActive: Optional[bool] = None

# Schema for the API response (output)
class VendorServiceResponse(VendorServiceBase):
    id: UUID
    vendorId: UUID
    vendorName: str
    rating: float
    reviewCount: int
    createdAt: datetime

    class Config:
        from_attributes = True # Pydantic v2, allows mapping from ORM models


class CouponBase(BaseModel):
    serviceId: UUID
    title: str = Field(..., min_length=3, max_length=100)
    discountType: str = "percentage"
    discountValue: float = Field(..., gt=0)
    validFrom: datetime
    validTo: datetime
    usageLimit: int = Field(..., gt=0)
    eligibility: Optional[str] = None
    terms: Optional[str] = None
    isActive: bool = True

class CouponCreate(CouponBase):
    code: str = Field(..., max_length=15)

class CouponUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    discountValue: Optional[float] = Field(None, gt=0)
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    usageLimit: Optional[int] = Field(None, gt=0)
    eligibility: Optional[str] = None
    terms: Optional[str] = None
    isActive: Optional[bool] = None

class Coupon(CouponBase):
    id: UUID  
    code: str
    usedCount: int
    createdAt: datetime

    class Config:
        from_attributes = True
