from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class PropertyResponse(BaseModel):
    id: UUID
    title: str
    # location: str

    model_config = ConfigDict(from_attributes=True)

class ExperienceBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: str = Field(..., max_length=1000)
    min_nights: int = Field(default=1, ge=0, description="Minimum nights required to be eligible")


class ExperienceCreate(ExperienceBase):
    property_ids: List[UUID] = Field(default_factory=list, description="List of property IDs to attach this experience to")


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = Field(None, max_length=1000)
    min_nights: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    property_ids: Optional[List[UUID]] = None


class ExperienceResponse(ExperienceBase):
    id: UUID
    host_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExperienceWithPropertiesResponse(ExperienceResponse):
    """Experience with attached property information."""
    property_count: int = 0
    properties: List[PropertyResponse] = []

    model_config = ConfigDict(from_attributes=True)
