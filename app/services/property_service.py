from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from uuid import UUID
from slugify import slugify
from datetime import datetime
from app.repositories.property_repository import PropertyRepository
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse
from app.models.property import Property


class PropertyService:
    def __init__(self, db: AsyncSession):
        self.repository = PropertyRepository(db)
    
    async def create_property(self, property_data: PropertyCreate, user_id: UUID) -> Property:
        """Create a new property listing."""
        # Generate unique slug
        base_slug = slugify(property_data.title)
        slug = base_slug
        counter = 1
        
        # Ensure slug is unique
        while await self.repository.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        property_obj = await self.repository.create(property_data, user_id, slug)
        
        # Set published_at if property is active
        if property_obj.is_active:
            property_obj.published_at = datetime.utcnow()
        
        return property_obj
    
    async def get_property(self, property_id: UUID) -> Optional[Property]:
        """Get property by ID."""
        return await self.repository.get_by_id(property_id)
    
    async def get_property_by_slug(self, slug: str) -> Optional[Property]:
        """Get property by slug."""
        return await self.repository.get_by_slug(slug)
    
    async def list_properties(
        self,
        skip: int,
        limit: int,
        filters: Optional[dict] = None
    ) -> Tuple[List[Property], int]:
        """List properties with filters."""
        return await self.repository.list_properties(skip, limit, filters)
    
    async def update_property(
        self,
        property_id: UUID,
        update_data: PropertyUpdate,
        user_id: UUID
    ) -> Optional[Property]:
        """Update property (owner only)."""
        property_obj = await self.repository.get_by_id(property_id)
        
        if not property_obj:
            return None
        
        # Check ownership
        if property_obj.user_id != user_id:
            raise PermissionError("You don't have permission to update this property")
        
        updated_property = await self.repository.update(property_id, update_data)
        
        # Update slug if title changed
        if update_data.title and updated_property:
            new_slug = slugify(update_data.title)
            if new_slug != updated_property.slug:
                # Ensure new slug is unique
                counter = 1
                slug = new_slug
                while await self.repository.get_by_slug(slug):
                    if slug == updated_property.slug:
                        break
                    slug = f"{new_slug}-{counter}"
                    counter += 1
                updated_property.slug = slug
        
        return updated_property
    
    async def delete_property(self, property_id: UUID, user_id: UUID) -> bool:
        """Delete property (owner only)."""
        property_obj = await self.repository.get_by_id(property_id)
        
        if not property_obj:
            return False
        
        # Check ownership
        if property_obj.user_id != user_id:
            raise PermissionError("You don't have permission to delete this property")
        
        return await self.repository.delete(property_id)
    
    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        limit: int = 20
    ) -> List[Property]:
        """Search properties near coordinates."""
        return await self.repository.search_nearby(latitude, longitude, radius_km, limit)
    
    async def get_featured_properties(self, limit: int = 10) -> List[Property]:
        """Get featured properties."""
        properties, _ = await self.repository.list_properties(
            skip=0,
            limit=limit,
            filters={'is_featured': True, 'is_active': True}
        )
        return properties
    
    async def get_user_properties(self, user_id: UUID, skip: int, limit: int) -> Tuple[List[Property], int]:
        """Get all properties owned by user."""
        return await self.repository.list_properties(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id}
        )