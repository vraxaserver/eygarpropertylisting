from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from uuid import UUID
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.models.experience import Experience


class ExperienceService:
    def __init__(self, db: AsyncSession):
        self.repository = ExperienceRepository(db)
    
    async def create_experience(self, experience_data: ExperienceCreate, host_id: UUID) -> Experience:
        """Create a new experience."""
        return await self.repository.create(experience_data, host_id)
    
    async def get_experience(self, experience_id: UUID) -> Optional[Experience]:
        """Get experience by ID."""
        return await self.repository.get_by_id(experience_id)
    
    async def list_host_experiences(
        self,
        host_id: UUID,
        skip: int,
        limit: int,
        active_only: bool = False
    ) -> Tuple[List[Experience], int]:
        """List experiences by host."""
        return await self.repository.list_by_host(host_id, skip, limit, active_only)
    
    async def update_experience(
        self,
        experience_id: UUID,
        update_data: ExperienceUpdate,
        host_id: UUID
    ) -> Optional[Experience]:
        """Update experience (host only)."""
        return await self.repository.update(experience_id, update_data, host_id)
    
    async def delete_experience(self, experience_id: UUID, host_id: UUID) -> bool:
        """Delete experience (host only)."""
        return await self.repository.delete(experience_id, host_id)
    
    async def get_property_experiences(self, property_id: UUID) -> List[Experience]:
        """Get all active experiences for a property."""
        return await self.repository.get_experiences_for_property(property_id)
    
    async def list_all_experiences(
        self,
        skip: int,
        limit: int,
        active_only: bool = True
    ) -> Tuple[List[Experience], int]:
        """List all experiences."""
        return await self.repository.list_all_experiences(skip, limit, active_only)


    async def add_properties_to_experience(
        self,
        experience_id: UUID,
        property_ids: List[UUID],
        host_id: UUID
    ) -> Experience:
        """Add properties to an existing experience."""
        return await self.repository.add_properties_to_experience(
            experience_id,
            property_ids,
            host_id
        )


    async def remove_property_from_experience(
        self,
        experience_id: UUID,
        property_id: UUID
    ) -> bool:
        """Remove a property from an experience."""
        return await self.repository.remove_property_from_experience(
            experience_id,
            property_id
        )
