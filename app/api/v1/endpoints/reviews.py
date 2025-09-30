from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.common import UserInfo, PaginatedResponse, MessageResponse
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.review_service import ReviewService


router = APIRouter()


@router.post("/properties/{property_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    property_id: UUID,
    review_data: ReviewCreate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a review for a property.
    Requires authentication. Users cannot review their own properties.
    """
    service = ReviewService(db)
    
    try:
        review = await service.create_review(property_id, current_user.id, review_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return review


@router.get("/properties/{property_id}/reviews", response_model=PaginatedResponse[ReviewResponse])
async def list_property_reviews(
    property_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    List all reviews for a property with pagination.
    Public endpoint - no authentication required.
    """
    service = ReviewService(db)
    reviews, total = await service.list_property_reviews(
        property_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    return PaginatedResponse.create(
        items=reviews,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    update_data: ReviewUpdate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a review (author only).
    Requires authentication.
    """
    service = ReviewService(db)
    
    try:
        review = await service.update_review(review_id, update_data, current_user.id)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.delete("/reviews/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: UUID,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a review (author only).
    Requires authentication.
    """
    service = ReviewService(db)
    
    try:
        deleted = await service.delete_review(review_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return MessageResponse(message="Review deleted successfully")


@router.post("/reviews/{review_id}/helpful", response_model=ReviewResponse)
async def mark_review_helpful(
    review_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a review as helpful.
    Public endpoint - no authentication required.
    """
    service = ReviewService(db)
    review = await service.mark_helpful(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review