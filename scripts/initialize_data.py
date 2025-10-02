"""
Script to initialize amenities and safety features from JSON files.
"""
import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.amenity import Amenity, SafetyFeature, AmenityCategory


async def load_amenities(session, json_file: str):
    """Load amenities from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            amenities_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {json_file}")
        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}: {e}")
        return 0
    
    # Handle both list and dict with 'amenities' key
    if isinstance(amenities_data, dict):
        amenities_data = amenities_data.get('amenities', [])
    
    if not isinstance(amenities_data, list):
        print(f"Error: Expected array of amenities, got {type(amenities_data)}")
        return 0
    
    count = 0
    for amenity_data in amenities_data:
        name = amenity_data.get('name')
        category = amenity_data.get('category', 'basic')
        icon = amenity_data.get('icon', '')
        
        if not name:
            print(f"Warning: Skipping amenity without name: {amenity_data}")
            continue
        
        # Check if already exists
        result = await session.execute(
            select(Amenity).where(Amenity.name == name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  Amenity '{name}' already exists, skipping")
            continue
        
        # Validate category
        try:
            category_enum = AmenityCategory(category.lower())
        except ValueError:
            print(f"  Warning: Invalid category '{category}' for amenity '{name}', using 'basic'")
            category_enum = AmenityCategory.BASIC
        
        # Create new amenity
        amenity = Amenity(
            name=name,
            category=category_enum,
            icon=icon
        )
        session.add(amenity)
        count += 1
        print(f"  + Added amenity: {name} ({category_enum.value})")
    
    await session.commit()
    return count


async def load_safety_features(session, json_file: str):
    """Load safety features from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            features_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {json_file}")
        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_file}: {e}")
        return 0
    
    # Handle both list and dict with 'safety_features' key
    if isinstance(features_data, dict):
        features_data = features_data.get('safety_features', features_data.get('safetyFeatures', []))
    
    if not isinstance(features_data, list):
        print(f"Error: Expected array of safety features, got {type(features_data)}")
        return 0
    
    count = 0
    for feature_data in features_data:
        name = feature_data.get('name')
        description = feature_data.get('description', '')
        icon = feature_data.get('icon', '')
        
        if not name:
            print(f"Warning: Skipping safety feature without name: {feature_data}")
            continue
        
        # Check if already exists
        result = await session.execute(
            select(SafetyFeature).where(SafetyFeature.name == name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  Safety feature '{name}' already exists, skipping")
            continue
        
        # Create new safety feature
        feature = SafetyFeature(
            name=name,
            description=description,
            icon=icon
        )
        session.add(feature)
        count += 1
        print(f"  + Added safety feature: {name}")
    
    await session.commit()
    return count


async def main():
    """Main initialization function."""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    # File paths
    amenities_file = Path(__file__).parent.parent / "data/amenities.json"
    safety_features_file = Path(__file__).parent.parent / "data/safety_features.json"
    
    async with AsyncSessionLocal() as session:
        try:
            # Load amenities
            print("\n[1/2] Loading amenities from amenities.json...")
            amenities_count = await load_amenities(session, str(amenities_file))
            
            # Load safety features
            print("\n[2/2] Loading safety features from safety_features.json...")
            features_count = await load_safety_features(session, str(safety_features_file))
            
            # Summary
            print("\n" + "=" * 60)
            print("Initialization Complete!")
            print("=" * 60)
            print(f"Amenities added: {amenities_count}")
            print(f"Safety features added: {features_count}")
            print(f"Total records: {amenities_count + features_count}")
            
        except Exception as e:
            print(f"\nError during initialization: {e}")
            await session.rollback()
            raise


if __name__ == '__main__':
    asyncio.run(main())