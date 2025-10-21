from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, exists
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from uuid import UUID
from slugify import slugify
from datetime import datetime, date
from app.repositories.property_repository import PropertyRepository
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse
from app.models.property import Property, Location
# from app.models.booking import Booking
from app.models.amenity import Amenity
from app.services.host_service import HostService


class PropertyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PropertyRepository(db)
        self.host_service = HostService()

    async def list_properties(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: dict = None
    ) -> Tuple[List[Property], int]:
        """List properties with advanced filtering."""
        filters = filters or {}

        # Base query
        query = select(Property).options(
            selectinload(Property.location),
            # selectinload(Property.host_id),
            # selectinload(Property.tags),
            selectinload(Property.images),
            selectinload(Property.amenities),
            selectinload(Property.experiences)
        )

        # Apply filters
        conditions = []

        # Active status
        if filters.get('is_active') is not None:
            conditions.append(Property.is_active == filters['is_active'])

        # Search filter (searches across multiple fields)
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            conditions.append(
                or_(
                    Property.title.ilike(search_term),
                    Property.description.ilike(search_term),
                    Property.location.has(Location.city.ilike(search_term)),
                    Property.location.has(Location.state.ilike(search_term)),
                    Property.location.has(Location.country.ilike(search_term)),
                    Property.location.has(Location.address.ilike(search_term))
                )
            )

        # Category filter
        if filters.get('category'):
            category = filters['category'].lower()
            # Search in title and description for category keywords
            conditions.append(
                or_(
                    Property.title.ilike(f"%{category}%"),
                    Property.description.ilike(f"%{category}%")
                )
            )

        # Date availability filter
        # if filters.get('check_in') and filters.get('check_out'):
        #     # Check if property is available for the date range
        #     # Exclude properties that have overlapping bookings
        #     subquery = (
        #         select(Booking.property_id)
        #         .where(
        #             and_(
        #                 Booking.property_id == Property.id,
        #                 Booking.status.in_(['confirmed', 'pending']),
        #                 or_(
        #                     and_(
        #                         Booking.check_in_date <= filters['check_in'],
        #                         Booking.check_out_date > filters['check_in']
        #                     ),
        #                     and_(
        #                         Booking.check_in_date < filters['check_out'],
        #                         Booking.check_out_date >= filters['check_out']
        #                     ),
        #                     and_(
        #                         Booking.check_in_date >= filters['check_in'],
        #                         Booking.check_out_date <= filters['check_out']
        #                     )
        #                 )
        #             )
        #         )
        #     )
        #     conditions.append(~Property.id.in_(subquery))

        # Guest capacity filters
        if filters.get('guests'):
            conditions.append(Property.max_guests >= filters['guests'])

        if filters.get('adults'):
            # Assuming adults + children should not exceed max_guests
            total_guests = filters['adults'] + filters.get('children', 0)
            conditions.append(Property.max_guests >= total_guests)

        # Property type filters
        if filters.get('property_type'):
            conditions.append(Property.property_type == filters['property_type'])

        if filters.get('place_type'):
            conditions.append(Property.place_type == filters['place_type'])

        if filters.get('property_types'):
            conditions.append(Property.place_type.in_(filters['property_types']))

        # Location filters
        if filters.get('city'):
            conditions.append(Property.location.has(Location.city.ilike(f"%{filters['city']}%")))

        if filters.get('country'):
            conditions.append(Property.location.has(Location.country.ilike(f"%{filters['country']}%")))

        # Price filters
        if filters.get('min_price') is not None:
            conditions.append(Property.price_per_night >= filters['min_price'])

        if filters.get('max_price') is not None:
            conditions.append(Property.price_per_night <= filters['max_price'])

        # Room filters
        if filters.get('bedrooms') is not None:
            conditions.append(Property.bedrooms >= filters['bedrooms'])

        if filters.get('beds') is not None:
            conditions.append(Property.beds >= filters['beds'])

        if filters.get('bathrooms') is not None:
            conditions.append(Property.bathrooms >= filters['bathrooms'])

        if filters.get('max_guests') is not None:
            conditions.append(Property.max_guests >= filters['max_guests'])

        # Amenities filter
        if filters.get('amenities'):
            amenity_ids = filters['amenities']
            # Property must have all selected amenities
            for amenity_id in amenity_ids:
                conditions.append(
                    Property.amenities.any(Amenity.id == amenity_id)
                )

        # Features
        if filters.get('instant_book') is not None:
            conditions.append(Property.instant_book == filters['instant_book'])

        if filters.get('has_experiences'):
            # Filter properties that have experiences
            conditions.append(Property.experiences.any())

        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Sorting
        sort_by = filters.get('sort_by', 'newest')
        if sort_by == 'price_asc':
            query = query.order_by(Property.price_per_night.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Property.price_per_night.desc())
        elif sort_by == 'rating':
            query = query.order_by(Property.average_rating.desc())
        else:  # newest
            query = query.order_by(Property.created_at.desc())

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        properties = result.scalars().all()

        return properties, total


    async def create_property(
        self,
        property_data: PropertyCreate,
        host_id: UUID,
        host_name: str,
        host_email: str,
        host_avatar: Optional[str] = None
    ) -> Property:
        """Create a new property listing with host information."""
        # Generate unique slug
        base_slug = slugify(property_data.title)
        slug = base_slug
        counter = 1

        # Ensure slug is unique
        while await self.repository.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        property_obj = await self.repository.create(
            property_data,
            host_id,
            host_name,
            host_email,
            host_avatar,
            slug
        )

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

    # async def list_properties(
    #     self,
    #     skip: int,
    #     limit: int,
    #     filters: Optional[dict] = None
    # ) -> Tuple[List[Property], int]:
    #     """List properties with filters."""
    #     return await self.repository.list_properties(skip, limit, filters)


    async def update_property(
        self,
        property_id: UUID,
        update_data: PropertyUpdate,
        host_id: UUID
    ) -> Optional[Property]:
        """Update property (owner only)."""
        property_obj = await self.repository.get_by_id(property_id)

        if not property_obj:
            return None

        # Check ownership
        if property_obj.host_id != host_id:
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

    async def delete_property(self, property_id: UUID, host_id: UUID) -> bool:
        """Delete property (owner only)."""
        property_obj = await self.repository.get_by_id(property_id)

        if not property_obj:
            return False

        # Check ownership
        if property_obj.host_id != host_id:
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

    async def get_host_properties(self, host_id: UUID, skip: int, limit: int) -> Tuple[List[Property], int]:
        """Get all properties owned by user."""
        return await self.repository.get_properties_by_host(
            host_id=host_id,
            skip=skip,
            limit=limit
        )
