from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.common import UserInfo, PaginatedResponse, MessageResponse
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceResponse,
    ExperienceWithPropertiesResponse
)
from app.services.experience_service import ExperienceService
from app.schemas.property import PropertyListResponse, PropertyResponse

router = APIRouter()


@router.post("/", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_data: ExperienceCreate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new experience.
    Requires authentication and host profile.
    """
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can create experiences"
        )

    service = ExperienceService(db)
    experience = await service.create_experience(experience_data, current_user.host_info.id)
    return experience


@router.get("/my-experiences", response_model=PaginatedResponse[ExperienceWithPropertiesResponse])
async def get_my_experiences(
    pagination: PaginationParams = Depends(),
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all experiences created by the authenticated host."""
    if not current_user.host_info or not current_user.host_info.id:
        return PaginatedResponse.create(
            items=[],
            total=0,
            page=pagination.page,
            page_size=pagination.page_size
        )

    service = ExperienceService(db)
    experiences, total = await service.list_host_experiences(
        current_user.host_info.id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    print(f"{'*' * 20}")
    print(experiences)
    return PaginatedResponse.create(
        items=experiences,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/{experience_id}", response_model=ExperienceWithPropertiesResponse)
async def get_experience(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get experience by ID."""
    service = ExperienceService(db)
    experience = await service.get_experience(experience_id)

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    return experience


@router.put("/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: UUID,
    update_data: ExperienceUpdate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update experience (host only)."""
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can update experiences"
        )

    service = ExperienceService(db)
    experience = await service.update_experience(
        experience_id,
        update_data,
        current_user.host_info.id
    )

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found or you don't have permission"
        )

    return experience


@router.delete("/{experience_id}", response_model=MessageResponse)
async def delete_experience(
    experience_id: UUID,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete experience (host only)."""
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can delete experiences"
        )

    service = ExperienceService(db)
    deleted = await service.delete_experience(experience_id, current_user.host_info.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found or you don't have permission"
        )

    return MessageResponse(message="Experience deleted successfully")


@router.get("/property/{property_id}/experiences", response_model=List[ExperienceResponse])
async def get_property_experiences(
    property_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all active experiences for a specific property."""
    service = ExperienceService(db)
    experiences = await service.get_property_experiences(property_id)
    return experiences


@router.get("/", response_model=PaginatedResponse[ExperienceResponse])
async def list_experiences(
    pagination: PaginationParams = Depends(),
    host_id: Optional[UUID] = Query(None, description="Filter by host ID"),
    active_only: bool = Query(True, description="Show only active experiences"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all experiences with optional filtering.
    Public endpoint - no authentication required.
    """
    service = ExperienceService(db)

    if host_id:
        # List experiences by specific host
        experiences, total = await service.list_host_experiences(
            host_id,
            skip=pagination.skip,
            limit=pagination.limit,
            active_only=active_only
        )
    else:
        # List all experiences
        experiences, total = await service.list_all_experiences(
            skip=pagination.skip,
            limit=pagination.limit,
            active_only=active_only
        )

    return PaginatedResponse.create(
        items=experiences,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.post("/{experience_id}/properties", response_model=ExperienceResponse)
async def add_properties_to_experience(
    experience_id: UUID,
    property_ids: List[UUID],
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add properties to an existing experience.
    Only the host who owns the experience can add properties.
    Only properties owned by the host can be added.
    """
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can add properties to experiences"
        )

    service = ExperienceService(db)

    # Verify experience exists and belongs to host
    experience = await service.get_experience(experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    if experience.host_id != current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this experience"
        )

    # Add properties
    updated_experience = await service.add_properties_to_experience(
        experience_id,
        property_ids,
        current_user.host_info.id
    )

    return updated_experience


@router.get("/{experience_id}/properties")
async def get_properties_for_experience(
    experience_id: UUID,
    pagination: PaginationParams = Depends(),
    # Depending on your business logic, you might want to allow any active user
    # or even the public to see the properties. Here, we restrict it to the owner.
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all properties associated with a specific experience.
    Only the host who owns the experience can view the associated properties.
    """
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a host"
        )

    service = ExperienceService(db)

    # Use the new service method to get the experience and its properties
    experience, _ = await service.get_experience_with_properties(experience_id)

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    # Authorization check: Ensure the current user owns the experience
    print("experience ==========================")
    print(experience[0])
    if experience[0].host_id != current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these properties"
        )

    # Because we eagerly loaded, this is now safe to return.
    # FastAPI will use the PropertyResponse schema to serialize each item.
    properties = experience[0].properties
    return properties
    # property_list = [PropertyResponse(property) for property in properties]

    # return PaginatedResponse.create(
    #     items=properties,
    #     total=len(properties),
    #     page=pagination.page,
    #     page_size=pagination.page_size
    # )

@router.delete("/{experience_id}/properties/{property_id}", response_model=MessageResponse)
async def remove_property_from_experience(
    experience_id: UUID,
    property_id: UUID,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a property from an experience.
    Only the host who owns the experience can remove properties.
    """
    if not current_user.host_info or not current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hosts can remove properties from experiences"
        )

    service = ExperienceService(db)

    # Verify experience exists and belongs to host
    experience = await service.get_experience(experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )

    if experience.host_id != current_user.host_info.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this experience"
        )

    # Remove property
    success = await service.remove_property_from_experience(
        experience_id,
        property_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found in this experience"
        )

    return MessageResponse(message="Property removed from experience successfully")
