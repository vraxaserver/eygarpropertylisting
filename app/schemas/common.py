from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime
from uuid import UUID


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class MessageResponse(BaseModel):
    """Standard message response."""
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    service: str
    version: str = "1.0.0"


class HostInfo(BaseModel):
    """Host information from auth service."""
    id: UUID
    status: Optional[str] = None
    completion_percentage: Optional[int] = None
    business_profile_completed: bool = False
    identity_verification_completed: bool = False
    contact_details_completed: bool = False
    review_submission_completed: bool = False
    next_step: Optional[str] = None
    review_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    """User information from auth service."""
    id: UUID
    email: str
    avatar_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_staff: bool = False
    is_superuser: bool = False
    host_info: Optional[HostInfo] = None
    
    class Config:
        from_attributes = True
        