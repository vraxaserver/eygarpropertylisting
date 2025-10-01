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
    id: UUID
    status: str
    completion_percentage: float
    business_profile_completed: bool
    identity_verification_completed: bool
    contact_details_completed: bool
    review_submission_completed: bool
    next_step: str
    review_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None


class UserInfo(BaseModel):
    """User information from auth service."""
    id: UUID  # Django typically uses UUID or int for user IDs
    email: str
    avatar_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_email_verified: bool = False
    is_staff: bool
    is_superuser: bool

    host_info: Optional[HostInfo] = None
    
    class Config:
        from_attributes = True