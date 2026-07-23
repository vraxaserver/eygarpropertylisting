import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.schemas.common import UserInfo
from tests.conftest import create_auth_header


@pytest.mark.asyncio
class TestAmenityEndpoints:
    """Test suite for amenity and safety feature endpoints."""

    @patch('app.dependencies.get_current_user')
    async def test_create_and_list_amenity(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo
    ):
        """Test creating and listing an amenity."""
        mock_get_user.return_value = test_user
        
        # 1. Create Amenity
        amenity_data = {
            "name": "Super WiFi",
            "category": "basic",
            "icon": "wifi"
        }
        headers = create_auth_header(test_user)
        response = await client.post("/api/v1/amenities", json=amenity_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Super WiFi"
        assert data["category"] == "basic"
        assert "id" in data

        # Try to recreate same amenity (should fail)
        response_dup = await client.post("/api/v1/amenities", json=amenity_data, headers=headers)
        assert response_dup.status_code == 400

        # 2. List Amenities
        response_list = await client.get("/api/v1/amenities")
        assert response_list.status_code == 200
        list_data = response_list.json()
        assert any(item["name"] == "Super WiFi" for item in list_data)

    @patch('app.dependencies.get_current_user')
    async def test_create_and_list_safety_feature(
        self,
        mock_get_user,
        client: AsyncClient,
        test_user: UserInfo
    ):
        """Test creating and listing a safety feature."""
        mock_get_user.return_value = test_user
        
        # 1. Create Safety Feature
        safety_data = {
            "name": "First Aid Kit Pro",
            "description": "Standard medical first aid kit.",
            "icon": "medkit"
        }
        headers = create_auth_header(test_user)
        response = await client.post("/api/v1/safety-features", json=safety_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "First Aid Kit Pro"
        assert "id" in data

        # Try to recreate same safety feature (should fail)
        response_dup = await client.post("/api/v1/safety-features", json=safety_data, headers=headers)
        assert response_dup.status_code == 400

        # 2. List Safety Features
        response_list = await client.get("/api/v1/safety-features")
        assert response_list.status_code == 200
        list_data = response_list.json()
        assert any(item["name"] == "First Aid Kit Pro" for item in list_data)
