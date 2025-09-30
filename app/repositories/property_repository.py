from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date
from app.models.property import Property, Location
from app.models.image import PropertyImage
from app.models.amenity import Amenity, SafetyFeature, property_amenities, property_safety_features
from app.models.rule import PropertyRule, RuleType
from app.schemas.property import PropertyCreate, PropertyUpdate


class PropertyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, property_data: PropertyCreate, user_id: UUID, slug: str) -> Property:
        """Create a new property with all related data."""
        # Create location
        print(f"Inside repository: user_id:{user_id}")
        location = Location(**property_data.location.model_dump())
        self.db.add(location)
        await self.db.flush()
        
        # Create property
        property_dict = property_data.model_dump(
            exclude={'location', 'amenity_ids', 'safety_feature_ids', 'images', 
                    'house_rules', 'cancellation_policy', 'check_in_policy'}
        )
        property_obj = Property(
            **property_dict,
            user_id=user_id,
            location_id=location.id,
            slug=slug
        )
        self.db.add(property_obj)
        await self.db.flush()
        
        # Add images
        for img_data in property_data.images:
            image = PropertyImage(
                **img_data.model_dump(),
                property_id=property_obj.id
            )
            self.db.add(image)
        
        # Add amenities using junction table directly
        if property_data.amenity_ids:
            from app.models.amenity import property_amenities
            for amenity_id in property_data.amenity_ids:
                stmt = property_amenities.insert().values(
                    property_id=property_obj.id,
                    amenity_id=amenity_id
                )
                await self.db.execute(stmt)
        
        # Add safety features using junction table directly
        if property_data.safety_feature_ids:
            from app.models.amenity import property_safety_features
            for safety_id in property_data.safety_feature_ids:
                stmt = property_safety_features.insert().values(
                    property_id=property_obj.id,
                    safety_feature_id=safety_id
                )
                await self.db.execute(stmt)
        
        # Add rules
        for rule_text in property_data.house_rules:
            rule = PropertyRule(
                property_id=property_obj.id,
                rule_text=rule_text,
                rule_type=RuleType.HOUSE_RULES
            )
            self.db.add(rule)
        
        if property_data.cancellation_policy:
            rule = PropertyRule(
                property_id=property_obj.id,
                rule_text=property_data.cancellation_policy,
                rule_type=RuleType.CANCELLATION_POLICY
            )
            self.db.add(rule)
        
        if property_data.check_in_policy:
            rule = PropertyRule(
                property_id=property_obj.id,
                rule_text=property_data.check_in_policy,
                rule_type=RuleType.CHECK_IN_POLICY
            )
            self.db.add(rule)
        
        await self.db.flush()
        await self.db.refresh(property_obj)
        return property_obj

    async def get_by_id(self, property_id: UUID) -> Optional[Property]:
        """Get property by ID with all relations."""
        result = await self.db.execute(
            select(Property)
            .options(
                joinedload(Property.location),
                selectinload(Property.images),
                selectinload(Property.amenities),
                selectinload(Property.safety_features),
                selectinload(Property.rules)
            )
            .where(Property.id == property_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Property]:
        """Get property by slug."""
        result = await self.db.execute(
            select(Property)
            .options(
                joinedload(Property.location),
                selectinload(Property.images),
                selectinload(Property.amenities),
                selectinload(Property.safety_features),
                selectinload(Property.rules)
            )
            .where(Property.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def list_properties(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[dict] = None
    ) -> Tuple[List[Property], int]:
        """List properties with filters and pagination."""
        query = select(Property).options(
            joinedload(Property.location),
            selectinload(Property.images)
        )
        
        # Apply filters
        conditions = []
        
        if filters:
            if filters.get('is_active') is not None:
                conditions.append(Property.is_active == filters['is_active'])
            
            if filters.get('is_featured'):
                conditions.append(Property.is_featured == True)
            
            if filters.get('property_type'):
                conditions.append(Property.property_type == filters['property_type'])
            
            if filters.get('min_price'):
                conditions.append(Property.price_per_night >= filters['min_price'])
            
            if filters.get('max_price'):
                conditions.append(Property.price_per_night <= filters['max_price'])
            
            if filters.get('bedrooms'):
                conditions.append(Property.bedrooms >= filters['bedrooms'])
            
            if filters.get('beds'):
                conditions.append(Property.beds >= filters['beds'])
            
            if filters.get('bathrooms'):
                conditions.append(Property.bathrooms >= filters['bathrooms'])
            
            if filters.get('max_guests'):
                conditions.append(Property.max_guests >= filters['max_guests'])
            
            if filters.get('instant_book'):
                conditions.append(Property.instant_book == True)
            
            if filters.get('city'):
                query = query.join(Property.location)
                conditions.append(Location.city.ilike(f"%{filters['city']}%"))
            
            if filters.get('country'):
                query = query.join(Property.location)
                conditions.append(Location.country.ilike(f"%{filters['country']}%"))
            
            if filters.get('user_id'):
                conditions.append(Property.user_id == filters['user_id'])
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(Property)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_by = filters.get('sort_by', 'newest') if filters else 'newest'
        if sort_by == 'price_asc':
            query = query.order_by(Property.price_per_night.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Property.price_per_night.desc())
        elif sort_by == 'rating':
            query = query.order_by(Property.average_rating.desc())
        else:  # newest
            query = query.order_by(Property.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        properties = list(result.scalars().all())
        
        return properties, total
    
    async def update(self, property_id: UUID, update_data: PropertyUpdate) -> Optional[Property]:
        """Update property."""
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return None
        
        update_dict = update_data.model_dump(
            exclude_unset=True, 
            exclude={'location', 'amenity_ids', 'safety_feature_ids'}
        )
        
        for field, value in update_dict.items():
            setattr(property_obj, field, value)
        
        # Update location if provided
        if update_data.location:
            location_dict = update_data.location.model_dump()
            for field, value in location_dict.items():
                setattr(property_obj.location, field, value)
        
        # Update amenities if provided - use direct junction table manipulation
        if update_data.amenity_ids is not None:
            from app.models.amenity import property_amenities
            from sqlalchemy import delete
            
            # Delete existing amenities
            delete_stmt = delete(property_amenities).where(
                property_amenities.c.property_id == property_id
            )
            await self.db.execute(delete_stmt)
            
            # Add new amenities
            for amenity_id in update_data.amenity_ids:
                insert_stmt = property_amenities.insert().values(
                    property_id=property_id,
                    amenity_id=amenity_id
                )
                await self.db.execute(insert_stmt)
        
        # Update safety features if provided
        if update_data.safety_feature_ids is not None:
            from app.models.amenity import property_safety_features
            from sqlalchemy import delete
            
            # Delete existing safety features
            delete_stmt = delete(property_safety_features).where(
                property_safety_features.c.property_id == property_id
            )
            await self.db.execute(delete_stmt)
            
            # Add new safety features
            for safety_id in update_data.safety_feature_ids:
                insert_stmt = property_safety_features.insert().values(
                    property_id=property_id,
                    safety_feature_id=safety_id
                )
                await self.db.execute(insert_stmt)
        
        await self.db.flush()
        await self.db.refresh(property_obj)
        return property_obj
    
    async def delete(self, property_id: UUID) -> bool:
        """Delete property."""
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return False
        
        await self.db.delete(property_obj)
        await self.db.flush()
        return True
    
    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        limit: int = 20
    ) -> List[Property]:
        """Search properties near coordinates."""
        # Haversine formula for distance calculation
        # Simplified version - for production, use PostGIS
        query = select(Property).options(
            joinedload(Property.location),
            selectinload(Property.images)
        ).join(Property.location).where(
            and_(
                Property.is_active == True,
                # Rough bounding box filter
                Location.latitude.between(latitude - radius_km/111, latitude + radius_km/111),
                Location.longitude.between(longitude - radius_km/111, longitude + radius_km/111)
            )
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())