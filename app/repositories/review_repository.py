from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Tuple
from uuid import UUID
from app.models.review import Review
from app.models.property import Property
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, property_id: UUID, user_id: UUID, review_data: ReviewCreate) -> Review:
        """Create a new review."""
        review = Review(
            **review_data.model_dump(),
            property_id=property_id,
            user_id=user_id
        )
        self.db.add(review)
        await self.db.flush()
        
        # Update property ratings
        await self.update_property_ratings(property_id)
        
        await self.db.refresh(review)
        return review
    
    async def get_by_id(self, review_id: UUID) -> Optional[Review]:
        """Get review by ID."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_property_and_user(self, property_id: UUID, user_id: UUID) -> Optional[Review]:
        """Check if user already reviewed this property."""
        result = await self.db.execute(
            select(Review).where(
                and_(
                    Review.property_id == property_id,
                    Review.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_property(
        self,
        property_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Review], int]:
        """List reviews for a property with pagination."""
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(Review).where(Review.property_id == property_id)
        )
        total = count_result.scalar()
        
        # Get reviews
        result = await self.db.execute(
            select(Review)
            .where(Review.property_id == property_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        reviews = list(result.scalars().all())
        
        return reviews, total
    
    async def update(self, review_id: UUID, update_data: ReviewUpdate) -> Optional[Review]:
        """Update review."""
        review = await self.get_by_id(review_id)
        if not review:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(review, field, value)
        
        await self.db.flush()
        
        # Update property ratings
        await self.update_property_ratings(review.property_id)
        
        await self.db.refresh(review)
        return review
    
    async def delete(self, review_id: UUID) -> bool:
        """Delete review."""
        review = await self.get_by_id(review_id)
        if not review:
            return False
        
        property_id = review.property_id
        await self.db.delete(review)
        await self.db.flush()
        
        # Update property ratings
        await self.update_property_ratings(property_id)
        
        return True
    
    async def increment_helpful(self, review_id: UUID) -> Optional[Review]:
        """Increment helpful count for review."""
        review = await self.get_by_id(review_id)
        if not review:
            return None
        
        review.helpful_count += 1
        await self.db.flush()
        await self.db.refresh(review)
        return review
    
    async def update_property_ratings(self, property_id: UUID):
        """Recalculate and update property average rating."""
        # Get all reviews for property
        result = await self.db.execute(
            select(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('total_reviews')
            )
            .where(Review.property_id == property_id)
        )
        stats = result.first()
        
        # Update property
        property_result = await self.db.execute(
            select(Property).where(Property.id == property_id)
        )
        property_obj = property_result.scalar_one_or_none()
        
        if property_obj:
            property_obj.average_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
            property_obj.total_reviews = stats.total_reviews if stats.total_reviews else 0
            await self.db.flush()