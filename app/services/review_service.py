from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from uuid import UUID
from app.repositories.review_repository import ReviewRepository
from app.repositories.property_repository import PropertyRepository
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.models.review import Review


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.repository = ReviewRepository(db)
        self.property_repository = PropertyRepository(db)
    
    async def create_review(
        self,
        property_id: UUID,
        user_id: UUID,
        review_data: ReviewCreate
    ) -> Review:
        """Create a new review."""
        # Check if property exists
        property_obj = await self.property_repository.get_by_id(property_id)
        if not property_obj:
            raise ValueError("Property not found")
        
        # Check if user is not the property owner
        if property_obj.user_id == user_id:
            raise ValueError("Property owners cannot review their own properties")
        
        # Check if user already reviewed this property
        existing_review = await self.repository.get_by_property_and_user(property_id, user_id)
        if existing_review:
            raise ValueError("You have already reviewed this property")
        
        return await self.repository.create(property_id, user_id, review_data)
    
    async def get_review(self, review_id: UUID) -> Optional[Review]:
        """Get review by ID."""
        return await self.repository.get_by_id(review_id)
    
    async def list_property_reviews(
        self,
        property_id: UUID,
        skip: int,
        limit: int
    ) -> Tuple[List[Review], int]:
        """List reviews for a property."""
        return await self.repository.list_by_property(property_id, skip, limit)
    
    async def update_review(
        self,
        review_id: UUID,
        update_data: ReviewUpdate,
        user_id: UUID
    ) -> Optional[Review]:
        """Update review (author only)."""
        review = await self.repository.get_by_id(review_id)
        
        if not review:
            return None
        
        # Check ownership
        if review.user_id != user_id:
            raise PermissionError("You don't have permission to update this review")
        
        return await self.repository.update(review_id, update_data)
    
    async def delete_review(self, review_id: UUID, user_id: UUID) -> bool:
        """Delete review (author only)."""
        review = await self.repository.get_by_id(review_id)
        
        if not review:
            return False
        
        # Check ownership
        if review.user_id != user_id:
            raise PermissionError("You don't have permission to delete this review")
        
        return await self.repository.delete(review_id)
    
    async def mark_helpful(self, review_id: UUID) -> Optional[Review]:
        """Mark review as helpful."""
        return await self.repository.increment_helpful(review_id)