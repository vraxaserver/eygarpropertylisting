"""
Script to insert properties from properties.json file.
Randomly assigns amenities and safety features from database.
"""
import asyncio
import sys
import json
import random
import httpx
from pathlib import Path
from typing import List, Dict, Optional
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.property import Property, Location, PropertyType, PlaceType
from app.models.image import PropertyImage
from app.models.amenity import Amenity, SafetyFeature, property_amenities, property_safety_features
from app.models.rule import PropertyRule, RuleType
from slugify import slugify


class PropertyInserter:
    def __init__(self):
        self.auth_service_url = "http://127.0.0.1:8000"
        self.host_cache = {}
    
    def fetch_host_info(self, host_id: str) -> Optional[Dict]:
        """Fetch host information from auth service."""
        if host_id in self.host_cache:
            return self.host_cache[host_id]
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.auth_service_url}/api/profiles/hosts/{host_id}/",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    host_data = response.json()
                    
                    # Extract eygar_host info
                    eygar_host = host_data.get('user_info')
                    if not eygar_host:
                        print(f"  Warning: Host {host_id} has no eygar_host data")
                        return None
                    
                    # Build host info
                    host_info = {
                        'host_id': eygar_host['id'],
                        'host_name': eygar_host.get('username', 'Host'),
                        'host_email': eygar_host.get('email', ''),
                        'host_avatar': eygar_host.get('avatar', '')
                    }
                    
                    self.host_cache[host_id] = host_info
                    return host_info
                else:
                    print(f"  Warning: Failed to fetch host {host_id}, status: {response.status_code}")
                    return None
        except Exception as e:
            print(f"  Error fetching host {host_id}: {e}")
            return None
    
    async def get_random_amenities(self, session, count: int = None) -> List[UUID]:
        """Get random amenity IDs from database."""
        result = await session.execute(select(Amenity))
        all_amenities = result.scalars().all()
        
        if not all_amenities:
            print("  Warning: No amenities found in database")
            return []
        
        if count is None:
            count = random.randint(3, min(8, len(all_amenities)))
        
        selected = random.sample(all_amenities, min(count, len(all_amenities)))
        return [amenity.id for amenity in selected]
    
    async def get_random_safety_features(self, session, count: int = None) -> List[UUID]:
        """Get random safety feature IDs from database."""
        result = await session.execute(select(SafetyFeature))
        all_features = result.scalars().all()
        
        if not all_features:
            print("  Warning: No safety features found in database")
            return []
        
        if count is None:
            count = random.randint(2, min(5, len(all_features)))
        
        selected = random.sample(all_features, min(count, len(all_features)))
        return [feature.id for feature in selected]
    
    def generate_unique_slug(self, title: str, existing_slugs: set) -> str:
        """Generate a unique slug for the property."""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        existing_slugs.add(slug)
        return slug
    
    async def insert_property(
        self, 
        session, 
        property_data: Dict, 
        host_ids: List[str],
        existing_slugs: set
    ) -> bool:
        """Insert a single property into the database."""
        try:
            # Select random host
            host_user_id = random.choice(host_ids)
            print("========= host_user_id: ", host_user_id)
            host_info = self.fetch_host_info(host_user_id)
            print("========= host_info: ", host_info)
            
            if not host_info:
                print(f"  Skipping property '{property_data.get('title')}' - couldn't fetch host info")
                return False
            
            # Check if property already exists by title
            title = property_data.get('title')
            result = await session.execute(
                select(Property).where(Property.title == title)
            )
            if result.scalar_one_or_none():
                print(f"  Property '{title}' already exists, skipping")
                return False
            
            # Generate unique slug
            slug = self.generate_unique_slug(title, existing_slugs)
            
            # Create location
            location_data = property_data.get('location', {})
            location = Location(
                address=location_data.get('address', 'N/A'),
                city=location_data.get('city', 'Unknown'),
                state=location_data.get('state', ''),
                country=location_data.get('country', 'Unknown'),
                postal_code=location_data.get('postal_code', ''),
                latitude=float(location_data.get('latitude', 0.0)),
                longitude=float(location_data.get('longitude', 0.0))
            )
            session.add(location)
            await session.flush()
            
            # Map property and place types
            property_type_str = property_data.get('property_type', 'house')
            place_type_str = property_data.get('place_type', 'entire_place')
            
            try:
                property_type = PropertyType(property_type_str)
            except ValueError:
                property_type = PropertyType.HOUSE
            
            try:
                place_type = PlaceType(place_type_str)
            except ValueError:
                place_type = PlaceType.ENTIRE_PLACE
            
            # Create property
            property_obj = Property(
                title=title,
                slug=slug,
                description=property_data.get('description', f"Beautiful {property_type_str} in {location_data.get('city', 'the city')}"),
                property_type=property_type,
                place_type=place_type,
                bedrooms=property_data.get('bedrooms', 1),
                beds=property_data.get('beds', 1),
                bathrooms=float(property_data.get('bathrooms', 1.0)),
                max_guests=property_data.get('max_guests', 2),
                max_adults=property_data.get('max_adults', property_data.get('max_guests', 2)),
                max_children=property_data.get('max_children', 0),
                max_infants=property_data.get('max_infants', 0),
                pets_allowed=property_data.get('pets_allowed', False),
                price_per_night=int(property_data.get('price_per_night', 10000)),
                currency=property_data.get('currency', 'USD'),
                cleaning_fee=int(property_data.get('cleaning_fee', 0)),
                service_fee=int(property_data.get('service_fee', 0)),
                weekly_discount=property_data.get('weekly_discount', 0),
                monthly_discount=property_data.get('monthly_discount', 0),
                instant_book=property_data.get('instant_book', False),
                is_active=property_data.get('is_active', True),
                is_featured=property_data.get('is_featured', False),
                location_id=location.id,
                host_id=UUID(host_info['host_id']),
                host_name=host_info['host_name'],
                host_email=host_info['host_email'],
                host_avatar=host_info['host_avatar']
            )
            session.add(property_obj)
            await session.flush()
            
            # Add images
            images = property_data.get('images', [])
            if not images:
                images = [
                    "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
                    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80"
                ]
            
            for idx, img_url in enumerate(images[:10]):
                image = PropertyImage(
                    property_id=property_obj.id,
                    image_url=img_url,
                    display_order=idx,
                    is_cover=(idx == 0),
                    alt_text=f"Property image {idx + 1}"
                )
                session.add(image)
            
            # Add random amenities
            amenity_ids = await self.get_random_amenities(session)
            for amenity_id in amenity_ids:
                stmt = property_amenities.insert().values(
                    property_id=property_obj.id,
                    amenity_id=amenity_id
                )
                await session.execute(stmt)
            
            # Add random safety features
            safety_ids = await self.get_random_safety_features(session)
            for safety_id in safety_ids:
                stmt = property_safety_features.insert().values(
                    property_id=property_obj.id,
                    safety_feature_id=safety_id
                )
                await session.execute(stmt)
            
            # Add house rules
            rules = property_data.get('rules', [
                "No smoking inside",
                "No parties or events",
                "Check-in after 3 PM"
            ])
            for rule_text in rules[:5]:
                rule = PropertyRule(
                    property_id=property_obj.id,
                    rule_text=rule_text,
                    rule_type=RuleType.HOUSE_RULES
                )
                session.add(rule)
            
            # Add cancellation policy
            cancellation = property_data.get('cancellation_policy', 'Free cancellation up to 48 hours before check-in')
            rule = PropertyRule(
                property_id=property_obj.id,
                rule_text=cancellation,
                rule_type=RuleType.CANCELLATION_POLICY
            )
            session.add(rule)
            
            # Add check-in policy
            checkin = property_data.get('check_in_policy', 'Check-in: 3:00 PM - 10:00 PM. Self check-in available.')
            rule = PropertyRule(
                property_id=property_obj.id,
                rule_text=checkin,
                rule_type=RuleType.CHECK_IN_POLICY
            )
            session.add(rule)
            
            await session.flush()
            
            print(f"  + Added: {title} (Host: {host_info['host_name']}, {len(amenity_ids)} amenities, {len(safety_ids)} safety features)")
            return True
            
        except Exception as e:
            print(f"  Error inserting property '{property_data.get('title')}': {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def load_properties(self):
        """Load properties from JSON file."""
        # Hardcoded path
        json_file = Path(__file__).parent.parent / "data/properties.json"
        
        print(f"\nLoading properties from {json_file}...")
        
        # Check if file exists
        if not json_file.exists():
            print(f"Error: File not found: {json_file}")
            print(f"Please create the file at: {json_file.absolute()}")
            return
        
        # Load JSON file
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            return
        
        # Extract properties and host_ids
        if isinstance(data, dict):
            properties = data.get('properties', [])
            host_ids = data.get('host_ids', [])
        else:
            print("Error: JSON must be an object with 'properties' and 'host_ids' keys")
            return
        
        if not properties:
            print("Error: No properties found in file")
            return
        
        if not host_ids:
            print("Error: No host_ids found in file. Please add 'host_ids' array to JSON")
            return
        
        print(f"Found {len(properties)} properties to insert")
        print(f"Using {len(host_ids)} hosts for random assignment")
        
        async with AsyncSessionLocal() as session:
            successful = 0
            failed = 0
            existing_slugs = set()
            
            for idx, property_data in enumerate(properties, 1):
                print(f"\n[{idx}/{len(properties)}] Processing '{property_data.get('title', 'Unknown')}'...")
                
                success = await self.insert_property(
                    session, 
                    property_data, 
                    host_ids,
                    existing_slugs
                )
                
                if success:
                    successful += 1
                else:
                    failed += 1
                
                # Commit every 10 properties
                if idx % 10 == 0:
                    await session.commit()
                    print(f"\n  Checkpoint: Committed {idx} properties")
            
            # Final commit
            await session.commit()
            
            # Summary
            print("\n" + "=" * 60)
            print("Property Insertion Complete!")
            print("=" * 60)
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            print(f"Total: {len(properties)}")


async def main():
    """Main function."""
    print("=" * 60)
    print("Property Insertion Script")
    print("=" * 60)
    print(f"Reading from: data/properties.json")
    
    inserter = PropertyInserter()
    await inserter.load_properties()


if __name__ == '__main__':
    asyncio.run(main())