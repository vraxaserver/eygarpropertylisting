import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from app.schemas.common import UserInfo
from app.models.property import Property, Location
from tests.conftest import create_auth_header, fake


@pytest.mark.asyncio
class TestPropertyEndpoints:
    """Test suite for property endpoints."""
    
    async def test_list_properties_empty(self, client: AsyncClient):
        """Test listing properties when database is empty."""
        response = await client.get("/api/v1/properties/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    async def test_list_properties(self, client: AsyncClient, test_property: Property):
        """Test listing properties."""
        response = await client.get("/api/v1/properties/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == str(test_property.id)
    
    async def test_get_property_by_id(self, client: AsyncClient, test_property: Property):
        """Test getting a property by ID."""
        response = await client.get(f"/api/v1/properties/{test_property.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_property.id)
        assert data["title"] == test_property.title
        assert data["property_type"] == test_property.property_type.value
    
    async def test_get_property_not_found(self, client: AsyncClient):
        """Test getting a non-existent property."""
        fake_id = uuid4()
        response = await client.get(f"/api/v1/properties/{fake_id}")
        assert response.status_code == 404
    
    @patch('app.dependencies.get_current_user')
    async def test_create_property(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo,
        test_amenities
    ):
        """Test creating a new property."""
        mock_get_user.return_value = test_user
        
        property_data = {
            "title": "Beautiful Beachfront Villa",
            "description": "A stunning villa with direct beach access and breathtaking ocean views. Perfect for families.",
            "property_type": "entire_place",
            "bedrooms": 3,
            "beds": 4,
            "bathrooms": 2.5,
            "max_guests": 6,
            "max_adults": 6,
            "max_children": 4,
            "max_infants": 2,
            "pets_allowed": True,
            "price_per_night": 25000,
            "currency": "USD",
            "cleaning_fee": 7500,
            "service_fee": 3000,
            "instant_book": True,
            "location": {
                "address": "123 Beach Road",
                "city": "Miami",
                "state": "Florida",
                "country": "USA",
                "postal_code": "33101",
                "latitude": 25.7617,
                "longitude": -80.1918
            },
            "amenity_ids": [str(test_amenities[0].id), str(test_amenities[1].id)],
            "safety_feature_ids": [],
            "images": [
                {"image_url": "https://example.com/image1.jpg", "display_order": 0, "is_cover": True, "alt_text": "Main view"},
                {"image_url": "https://example.com/image2.jpg", "display_order": 1, "is_cover": False, "alt_text": "Kitchen"},
                {"image_url": "https://example.com/image3.jpg", "display_order": 2, "is_cover": False, "alt_text": "Bedroom"}
            ],
            "house_rules": ["No smoking", "No parties", "Check-in after 3 PM"],
            "cancellation_policy": "Free cancellation up to 48 hours before check-in",
            "check_in_policy": "Self check-in with lockbox"
        }
        
        headers = create_auth_header(test_user)
        response = await client.post("/api/v1/properties/", json=property_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == property_data["title"]
        assert data["user_id"] == str(test_user.id)
        assert len(data["images"]) == 3
    
    @patch('app.dependencies.get_current_user')
    async def test_create_property_insufficient_images(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo
    ):
        """Test creating property with less than 3 images fails."""
        mock_get_user.return_value = test_user
        
        property_data = {
            "title": "Test Property",
            "description": "A test property with insufficient images for validation testing.",
            "property_type": "private_room",
            "price_per_night": 10000,
            "location": {
                "address": "123 Test St",
                "city": "Test City",
                "country": "Test Country",
                "latitude": 0.0,
                "longitude": 0.0
            },
            "images": [
                {"image_url": "https://example.com/image1.jpg", "display_order": 0}
            ]
        }
        
        headers = create_auth_header(test_user)
        response = await client.post("/api/v1/properties/", json=property_data, headers=headers)
        
        assert response.status_code == 422
    
    @patch('app.dependencies.get_current_user')
    async def test_update_property(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo,
        test_property: Property
    ):
        """Test updating a property."""
        mock_get_user.return_value = test_user
        
        update_data = {
            "title": "Updated Property Title",
            "price_per_night": 20000,
            "bedrooms": 3
        }
        
        headers = create_auth_header(test_user)
        response = await client.put(
            f"/api/v1/properties/{test_property.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["price_per_night"] == update_data["price_per_night"]
        assert data["bedrooms"] == update_data["bedrooms"]
    
    @patch('app.dependencies.get_current_user')
    async def test_update_property_not_owner(
        self,
        mock_get_user,
        client: AsyncClient,
        another_user: UserInfo,
        test_property: Property
    ):
        """Test updating property by non-owner fails."""
        mock_get_user.return_value = another_user
        
        update_data = {"title": "Unauthorized Update"}
        headers = create_auth_header(another_user)
        
        response = await client.put(
            f"/api/v1/properties/{test_property.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 403
    
    @patch('app.dependencies.get_current_user')
    async def test_delete_property(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo,
        test_property: Property
    ):
        """Test deleting a property."""
        mock_get_user.return_value = test_user
        
        headers = create_auth_header(test_user)
        response = await client.delete(
            f"/api/v1/properties/{test_property.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Verify property is deleted
        get_response = await client.get(f"/api/v1/properties/{test_property.id}")
        assert get_response.status_code == 404
    
    async def test_search_properties(self, client: AsyncClient, test_property: Property):
        """Test searching properties with filters."""
        response = await client.get(
            "/api/v1/properties/search",
            params={
                "min_price": 10000,
                "max_price": 20000,
                "bedrooms": 2,
                "sort_by": "price_asc"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    async def test_get_featured_properties(self, client: AsyncClient, test_property: Property):
        """Test getting featured properties."""
        # Update property to be featured
        test_property.is_featured = True
        
        response = await client.get("/api/v1/properties/featured")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    async def test_get_nearby_properties(self, client: AsyncClient, test_property: Property):
        """Test searching properties near coordinates."""
        response = await client.get(
            "/api/v1/properties/nearby",
            params={
                "lat": test_property.location.latitude,
                "lng": test_property.location.longitude,
                "radius": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    async def test_pagination(self, client: AsyncClient, db_session, test_user: UserInfo, test_location: Location):
        """Test pagination of property listings."""
        # Create multiple properties
        from app.models.property import Property, PropertyType, VerificationStatus
        
        for i in range(25):
            prop = Property(
                title=f"Test Property {i}",
                slug=f"test-property-{i}",
                description="Test description with enough characters to pass validation requirements.",
                property_type=PropertyType.ENTIRE_PLACE,
                bedrooms=2,
                beds=2,
                bathrooms=1.0,
                max_guests=4,
                max_adults=4,
                max_children=2,
                max_infants=1,
                price_per_night=15000,
                currency="USD",
                location_id=test_location.id,
                user_id=test_user.id,
                is_active=True,
                verification_status=VerificationStatus.VERIFIED
            )
            db_session.add(prop)
        
        await db_session.commit()
        
        # Test first page
        response = await client.get("/api/v1/properties/?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["total_pages"] == 3
        
        # Test second page
        response = await client.get("/api/v1/properties/?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10