from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from app.models.amenity import AmenityCategory


class AmenityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: AmenityCategory
    icon: Optional[str] = Field(None, max_length=50)


class AmenityCreate(AmenityBase):
    pass


class AmenityResponse(AmenityBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class SafetyFeatureBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)


class SafetyFeatureCreate(SafetyFeatureBase):
    pass


class SafetyFeatureResponse(SafetyFeatureBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)