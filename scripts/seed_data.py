"""
Seed script to populate database with sample data for development and testing.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.database import AsyncSessionLocal
from app.models import (
    Amenity, SafetyFeature, AmenityCategory, Location, Property,
    PropertyImage, PropertyRule, RuleType, PropertyType, VerificationStatus
)


async def seed_amenities(session: AsyncSession):
    """Seed amenities."""
    amenities_data = [
        # Basic
        ("WiFi", AmenityCategory.BASIC, "📶"),
        ("Air Conditioning", AmenityCategory.BASIC, "❄️"),
        ("Heating", AmenityCategory.BASIC, "🔥"),
        ("Workspace", AmenityCategory.BASIC, "💻"),
        ("TV", AmenityCategory.ENTERTAINMENT, "📺"),
        ("Washer", AmenityCategory.BASIC, "🧺"),
        ("Dryer", AmenityCategory.BASIC, "🌀"),
        ("Free Parking", AmenityCategory.BASIC, "🅿️"),
        ("Pool", AmenityCategory.ENTERTAINMENT, "🏊"),
        ("Hot Tub", AmenityCategory.ENTERTAINMENT, "🛁"),
        
        # Kitchen
        ("Kitchen", AmenityCategory.KITCHEN, "🍳"),
        ("Refrigerator", AmenityCategory.KITCHEN, "🧊"),
        ("Microwave", AmenityCategory.KITCHEN, "📡"),
        ("Dishwasher", AmenityCategory.KITCHEN, "🍽️"),
        ("Coffee Maker", AmenityCategory.KITCHEN, "☕"),
        ("Cooking Basics", AmenityCategory.KITCHEN, "🥘"),
        
        # Entertainment
        ("Netflix", AmenityCategory.ENTERTAINMENT, "📺"),
        ("Gaming Console", AmenityCategory.ENTERTAINMENT, "🎮"),
        ("Board Games", AmenityCategory.ENTERTAINMENT, "🎲"),
        ("Piano", AmenityCategory.ENTERTAINMENT, "🎹"),
        
        # Safety
        ("Fire Extinguisher", AmenityCategory.SAFETY, "🧯"),
        ("Security Cameras", AmenityCategory.SAFETY, "📹"),
        
        # Accessibility
        ("Step-free Entry", AmenityCategory.ACCESSIBILITY, "♿"),
        ("Wide Doorways", AmenityCategory.ACCESSIBILITY, "🚪"),
        ("Accessible Bathroom", AmenityCategory.ACCESSIBILITY, "🚻"),
    ]
    
    for name, category, icon in amenities_data:
        amenity = Amenity(name=name, category=category, icon=icon)
        session.add(amenity)
    
    await session.commit()
    print(f"✅ Seeded {len(amenities_data)} amenities")


async def seed_safety_features(session: AsyncSession):
    """Seed safety features."""
    safety_data = [
        ("Smoke Alarm", "Working smoke detector", "🚨"),
        ("Carbon Monoxide Alarm", "Working CO detector", "⚠️"),
        ("First Aid Kit", "Basic first aid supplies", "🏥"),
        ("Fire Extinguisher", "Accessible fire extinguisher", "🧯"),
        ("Enhanced Clean", "Enhanced cleaning protocol", "✨"),
        ("Self Check-in", "Contactless check-in available", "🔑"),
    ]
    
    for name, description, icon in safety_data:
        feature = SafetyFeature(name=name, description=description, icon=icon)
        session.add(feature)
    
    await session.commit()
    print(f"✅ Seeded {len(safety_data)} safety features")


async def seed_sample_properties(session: AsyncSession):
    """Seed sample properties."""
    
    # Create sample locations
    locations = [
        Location(
            address="123 Beach Road",
            city="Miami",
            state="Florida",
            country="USA",
            postal_code="33101",
            latitude=25.7617,
            longitude=-80.1918
        ),
        Location(
            address="456 Mountain View",
            city="Denver",
            state="Colorado",
            country="USA",
            postal_code="80202",
            latitude=39.7392,
            longitude=-104.9903
        ),
        Location(
            address="789 City Center",
            city="New York",
            state="New York",
            country="USA",
            postal_code="10001",
            latitude=40.7128,
            longitude=-74.0060
        ),
    ]
    
    for location in locations:
        session.add(location)
    await session.flush()
    
    # Sample properties
    properties_data = [
        {
            "title": "Luxury Beachfront Villa with Ocean Views",
            "slug": "luxury-beachfront-villa-miami",
            "description": "Experience paradise in this stunning beachfront villa. Wake up to breathtaking ocean views, enjoy direct beach access, and relax in your private infinity pool. This spacious 4-bedroom villa is perfect for families or groups looking for the ultimate Miami Beach experience.",
            "property_type": PropertyType.ENTIRE_PLACE,
            "bedrooms": 4,
            "beds": 5,
            "bathrooms": 3.5,
            "max_guests": 8,
            "max_adults": 8,
            "max_children": 4,
            "max_infants": 2,
            "pets_allowed": False,
            "price_per_night": 45000,  # $450
            "currency": "USD",
            "cleaning_fee": 15000,
            "service_fee": 5000,
            "location_id": locations[0].id,
            "is_featured": True,
            "verification_status": VerificationStatus.VERIFIED,
            "instant_book": True,
        },
        {
            "title": "Cozy Mountain Cabin with Hot Tub",
            "slug": "cozy-mountain-cabin-denver",
            "description": "Escape to the mountains in this charming cabin. Perfect for a romantic getaway or small family retreat. Features include a wood-burning fireplace, private hot tub, and stunning mountain views. Close to hiking trails and ski resorts.",
            "property_type": PropertyType.ENTIRE_PLACE,
            "bedrooms": 2,
            "beds": 3,
            "bathrooms": 2.0,
            "max_guests": 4,
            "max_adults": 4,
            "max_children": 2,
            "max_infants": 1,
            "pets_allowed": True,
            "price_per_night": 22000,  # $220
            "currency": "USD",
            "cleaning_fee": 8000,
            "service_fee": 3000,
            "weekly_discount": 10,
            "location_id": locations[1].id,
            "is_featured": True,
            "verification_status": VerificationStatus.VERIFIED,
            "instant_book": False,
        },
        {
            "title": "Modern Downtown Loft - Times Square",
            "slug": "modern-downtown-loft-nyc",
            "description": "Stay in the heart of Manhattan in this sleek, modern loft. Walking distance to Times Square, Broadway theaters, and world-class restaurants. Features floor-to-ceiling windows, designer furnishings, and all the amenities you need for a perfect NYC stay.",
            "property_type": PropertyType.ENTIRE_PLACE,
            "bedrooms": 1,
            "beds": 1,
            "bathrooms": 1.0,
            "max_guests": 2,
            "max_adults": 2,
            "max_children": 0,
            "max_infants": 0,
            "pets_allowed": False,
            "price_per_night": 28000,  # $280
            "currency": "USD",
            "cleaning_fee": 10000,
            "service_fee": 4000,
            "monthly_discount": 15,
            "location_id": locations[2].id,
            "is_featured": False,
            "verification_status": VerificationStatus.VERIFIED,
            "instant_book": True,
        },
    ]
    
    # Create sample user IDs (in production, these would be real user IDs)
    sample_user_ids = [uuid4() for _ in range(3)]
    
    for idx, prop_data in enumerate(properties_data):
        prop_data["user_id"] = sample_user_ids[idx]
        property_obj = Property(**prop_data)
        session.add(property_obj)
        await session.flush()
        
        # Add sample images
        images = [
            PropertyImage(
                property_id=property_obj.id,
                image_url=f"https://images.unsplash.com/photo-{1500000000000+idx}?w=800",
                display_order=0,
                is_cover=True,
                alt_text="Main view"
            ),
            PropertyImage(
                property_id=property_obj.id,
                image_url=f"https://images.unsplash.com/photo-{1500000000001+idx}?w=800",
                display_order=1,
                is_cover=False,
                alt_text="Living room"
            ),
            PropertyImage(
                property_id=property_obj.id,
                image_url=f"https://images.unsplash.com/photo-{1500000000002+idx}?w=800",
                display_order=2,
                is_cover=False,
                alt_text="Bedroom"
            ),
        ]
        for img in images:
            session.add(img)
        
        # Add property rules
        rules = [
            PropertyRule(
                property_id=property_obj.id,
                rule_text="No smoking inside the property",
                rule_type=RuleType.HOUSE_RULES
            ),
            PropertyRule(
                property_id=property_obj.id,
                rule_text="Quiet hours: 10 PM - 8 AM",
                rule_type=RuleType.HOUSE_RULES
            ),
            PropertyRule(
                property_id=property_obj.id,
                rule_text="Free cancellation up to 48 hours before check-in",
                rule_type=RuleType.CANCELLATION_POLICY
            ),
            PropertyRule(
                property_id=property_obj.id,
                rule_text="Check-in: 3:00 PM - 10:00 PM",
                rule_type=RuleType.CHECK_IN_POLICY
            ),
        ]
        for rule in rules:
            session.add(rule)
    
    await session.commit()
    print(f"✅ Seeded {len(properties_data)} sample properties")


async def main():
    """Main seed function."""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            await seed_amenities(session)
            await seed_safety_features(session)
            await seed_sample_properties(session)
            
            print("\n✅ Database seeding completed successfully!")
            print("\n📝 Sample data includes:")
            print("   - 20+ amenities across all categories")
            print("   - 6 safety features")
            print("   - 3 sample properties with images and rules")
            print("\n🚀 You can now start the FastAPI server and test the API!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())