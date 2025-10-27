from sqlalchemy import and_, delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.experience import Experience, property_experiences
from app.models.property import Property  # Assuming Property model is in app.models.property
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.schemas.property import PropertyListResponse


class ExperienceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, experience_data: ExperienceCreate, host_id: UUID) -> Experience:
        """Create a new experience."""
        experience = Experience(
            title=experience_data.title,
            description=experience_data.description,
            image_url=experience_data.image_url,
            min_nights=experience_data.min_nights,
            host_id=host_id
        )
        self.db.add(experience)
        await self.db.flush()

        # Attach to properties
        if experience_data.property_ids:
            await self.attach_to_properties(experience.id, experience_data.property_ids, host_id)

        await self.db.refresh(experience)
        return experience

    async def get_by_id(self, experience_id: UUID) -> Optional[Experience]:
        """Get experience by ID."""
        result = await self.db.execute(
            select(Experience)
            .options(selectinload(Experience.properties))
            .where(Experience.id == experience_id)
        )
        return result.scalar_one_or_none()

    async def list_by_host(
        self,
        host_id: UUID,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = False
    ) -> Tuple[List[Experience], int]:
        """List experiences by host."""
        query = select(Experience).where(Experience.host_id == host_id).options(selectinload(Experience.properties)) # Eager load properties

        if active_only:
            query = query.where(Experience.is_active == True)

        # Count
        count_query = select(func.count(Experience.id)).where(Experience.host_id == host_id)
        if active_only:
            count_query = count_query.where(Experience.is_active == True)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get experiences
        query = query.order_by(Experience.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        experiences = list(result.scalars().all())

        return experiences, total

    async def update(self, experience_id: UUID, update_data: ExperienceUpdate, host_id: UUID) -> Optional[Experience]:
        """Update experience."""
        experience = await self.get_by_id(experience_id)
        if not experience or experience.host_id != host_id:
            return None

        update_dict = update_data.model_dump(exclude_unset=True, exclude={'property_ids'})
        for field, value in update_dict.items():
            setattr(experience, field, value)

        # Update property attachments if provided
        if update_data.property_ids is not None:
            # Remove all existing attachments
            delete_stmt = delete(property_experiences).where(
                property_experiences.c.experience_id == experience_id
            )
            await self.db.execute(delete_stmt)

            # Add new attachments
            await self.attach_to_properties(experience_id, update_data.property_ids, host_id)

        await self.db.flush()
        await self.db.refresh(experience)
        return experience

    async def delete(self, experience_id: UUID, host_id: UUID) -> bool:
        """Delete experience."""
        experience = await self.get_by_id(experience_id)
        if not experience or experience.host_id != host_id:
            return False

        await self.db.delete(experience)
        await self.db.flush()
        return True

    async def attach_to_properties(self, experience_id: UUID, property_ids: List[UUID], host_id: UUID):
        """Attach experience to properties (only host's properties)."""
        for property_id in property_ids:
            # Verify property belongs to host
            result = await self.db.execute(
                select(Property).where(
                    and_(
                        Property.id == property_id,
                        Property.host_id == host_id
                    )
                )
            )
            property_obj = result.scalar_one_or_none()

            if property_obj:
                stmt = property_experiences.insert().values(
                    experience_id=experience_id,
                    property_id=property_id
                )
                await self.db.execute(stmt)

    async def get_experiences_for_property(self, property_id: UUID) -> List[Experience]:
        """Get all active experiences for a property."""
        result = await self.db.execute(
            select(Experience)
            .join(property_experiences)
            .where(
                and_(
                    property_experiences.c.property_id == property_id,
                    Experience.is_active == True
                )
            )
            .order_by(Experience.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all_experiences(
        self,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True
    ) -> Tuple[List[Experience], int]:
        """List all experiences with optional active filter."""
        query = select(Experience)

        if active_only:
            query = query.where(Experience.is_active == True)

        # Count
        count_query = select(func.count(Experience.id))
        if active_only:
            count_query = count_query.where(Experience.is_active == True)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get experiences
        query = query.order_by(Experience.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        experiences = list(result.scalars().all())

        return experiences, total


    async def add_properties_to_experience(
        self,
        experience_id: UUID,
        property_ids: List[UUID],
        host_id: UUID
    ) -> Experience:
        """Add additional properties to an existing experience."""
        # Get existing property associations
        existing_result = await self.db.execute(
            select(property_experiences.c.property_id)
            .where(property_experiences.c.experience_id == experience_id)
        )
        existing_property_ids = set(row[0] for row in existing_result.all())

        # Add only new properties
        new_property_ids = [pid for pid in property_ids if pid not in existing_property_ids]

        if new_property_ids:
            await self.attach_to_properties(experience_id, new_property_ids, host_id)
            await self.db.flush() # Persist the new associations

        # Return updated experience
        return await self.get_by_id(experience_id)


    async def remove_property_from_experience(
        self,
        experience_id: UUID,
        property_id: UUID
    ) -> bool:
        """Remove a property from an experience."""
        delete_stmt = delete(property_experiences).where(
            and_(
                property_experiences.c.experience_id == experience_id,
                property_experiences.c.property_id == property_id
            )
        )
        result = await self.db.execute(delete_stmt)
        await self.db.flush()

        return result.rowcount > 0

    async def get_properties_by_experience(
        self,
        experience_id: UUID
    ) -> PropertyListResponse:
        query = (
            select(Experience)
            .options(selectinload(Experience.properties)) # <-- Eagerly loads properties
            .where(Experience.id == experience_id)
        )
        result = await self.db.execute(query)
        properties = list(result.scalars().all())

        return properties, len(properties)
