import pytest
from httpx import AsyncClient
from unittest.mock import patch
from uuid import uuid4

from app.schemas.common import UserInfo
from app.models.property import Property
from app.models.review import Review
from tests.conftest import create_auth_header


@pytest.mark.asyncio
class TestReviewEndpoints:
    """Test suite for review endpoints."""
    
    @patch('app.dependencies.get_current_user')
    async def test_create_review(
        self,
        mock_get_user,
        client: AsyncClient,
        another_user: UserInfo,
        test_property: Property
    ):
        """Test creating a review."""
        mock_get_user.return_value = another_user
        
        review_data = {
            "rating": 5,
            "comment": "Amazing property! Everything was perfect.",
            "cleanliness_rating": 5,
            "accuracy_rating": 5,
            "communication_rating": 5,
            "location_rating": 5,
            "check_in_rating": 5,
            "value_rating": 5
        }
        
        headers = create_auth_header(another_user)
        response = await client.post(
            f"/api/v1/properties/{test_property.id}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == review_data["rating"]
        assert data["comment"] == review_data["comment"]
        assert data["user_id"] == str(another_user.id)
    
    @patch('app.dependencies.get_current_user')
    async def test_create_review_own_property(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo,
        test_property: Property
    ):
        """Test that owners cannot review their own properties."""
        mock_get_user.return_value = test_user
        
        review_data = {
            "rating": 5,
            "comment": "My own property is great!"
        }
        
        headers = create_auth_header(test_user)
        response = await client.post(
            f"/api/v1/properties/{test_property.id}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "cannot review their own" in response.json()["detail"].lower()
    
    @patch('app.dependencies.get_current_user')
    async def test_create_duplicate_review(
        self,
        mock_get_user,
        client: AsyncClient,
        another_user: UserInfo,
        test_property: Property,
        db_session
    ):
        """Test that users cannot review the same property twice."""
        mock_get_user.return_value = another_user
        
        # Create first review
        review = Review(
            property_id=test_property.id,
            user_id=another_user.id,
            rating=5,
            comment="First review"
        )
        db_session.add(review)
        await db_session.commit()
        
        # Try to create second review
        review_data = {
            "rating": 4,
            "comment": "Second review attempt"
        }
        
        headers = create_auth_header(another_user)
        response = await client.post(
            f"/api/v1/properties/{test_property.id}/reviews",
            json=review_data,
            headers=headers
        )
        
        assert response.status_code == 400
        assert "already reviewed" in response.json()["detail"].lower()
    
    async def test_list_property_reviews(
        self,
        client: AsyncClient,
        test_property: Property,
        another_user: UserInfo,
        db_session
    ):
        """Test listing reviews for a property."""
        # Create multiple reviews
        for i in range(5):
            review = Review(
                property_id=test_property.id,
                user_id=uuid4(),
                rating=4 + (i % 2),
                comment=f"Review {i}"
            )
            db_session.add(review)
        await db_session.commit()
        
        response = await client.get(f"/api/v1/properties/{test_property.id}/reviews")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
    
    @patch('app.dependencies.get_current_user')
    async def test_update_review(
        self,
        mock_get_user,
        client: AsyncClient,
        another_user: UserInfo,
        test_property: Property,
        db_session
    ):
        """Test updating a review."""
        mock_get_user.return_value = another_user
        
        # Create review
        review = Review(
            property_id=test_property.id,
            user_id=another_user.id,
            rating=4,
            comment="Original comment"
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        # Update review
        update_data = {
            "rating": 5,
            "comment": "Updated comment with better rating"
        }
        
        headers = create_auth_header(another_user)
        response = await client.put(
            f"/api/v1/reviews/{review.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == update_data["rating"]
        assert data["comment"] == update_data["comment"]
    
    @patch('app.dependencies.get_current_user')
    async def test_update_review_not_author(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo,
        another_user: UserInfo,
        test_property: Property,
        db_session
    ):
        """Test that non-authors cannot update reviews."""
        mock_get_user.return_value = test_user
        
        # Create review by another_user
        review = Review(
            property_id=test_property.id,
            user_id=another_user.id,
            rating=4,
            comment="Original comment"
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        # Try to update as different user
        update_data = {"rating": 5}
        headers = create_auth_header(test_user)
        
        response = await client.put(
            f"/api/v1/reviews/{review.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 403
    
    @patch('app.dependencies.get_current_user')
    async def test_delete_review(
        self,
        mock_get_user,
        client: AsyncClient,
        another_user: UserInfo,
        test_property: Property,
        db_session
    ):
        """Test deleting a review."""
        mock_get_user.return_value = another_user
        
        # Create review
        review = Review(
            property_id=test_property.id,
            user_id=another_user.id,
            rating=4,
            comment="To be deleted"
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        headers = create_auth_header(another_user)
        response = await client.delete(
            f"/api/v1/reviews/{review.id}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    async def test_mark_review_helpful(
        self,
        client: AsyncClient,
        test_property: Property,
        another_user: UserInfo,
        db_session
    ):
        """Test marking a review as helpful."""
        # Create review
        review = Review(
            property_id=test_property.id,
            user_id=another_user.id,
            rating=5,
            comment="Helpful review",
            helpful_count=0
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        response = await client.post(f"/api/v1/reviews/{review.id}/helpful")
        
        assert response.status_code == 200
        data = response.json()
        assert data["helpful_count"] == 1
    
    async def test_review_updates_property_rating(
        self,
        client: AsyncClient,
        test_property: Property,
        db_session
    ):
        """Test that adding reviews updates property average rating."""
        # Create multiple reviews
        ratings = [5, 4, 5, 3, 4]
        for rating in ratings:
            review = Review(
                property_id=test_property.id,
                user_id=uuid4(),
                rating=rating,
                comment=f"Rating {rating}"
            )
            db_session.add(review)
        await db_session.commit()
        
        # Refresh property
        await db_session.refresh(test_property)
        
        # Check average rating
        expected_avg = sum(ratings) / len(ratings)
        assert test_property.average_rating == pytest.approx(expected_avg, 0.1)
        assert test_property.total_reviews == len(ratings)