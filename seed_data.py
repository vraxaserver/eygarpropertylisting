import uuid
import random
import logging
from datetime import datetime, timedelta, UTC
from faker import Faker

# --- Setup SQLAlchemy & Imports (Replace with your actual app imports) ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# NOTE: In your actual app, import these from your files:
from app.database import Base, engine, AsyncSessionLocal
from app.models.amenity import Amenity, AmenityCategory, SafetyFeature
from app.models.property import Property, Location, PropertyType, PlaceType, VerificationStatus
from app.models.image import PropertyImage
from app.models.rule import PropertyRule, RuleType
from app.models.review import Review

# For this standalone demonstration, we define a Mock DB setup and include models:
print("Setting up database connection and models...")
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# --- PASTE YOUR MODEL DEFINITIONS HERE IF RUNNING STANDALONE ---
# (For brevity, I am assuming the classes provided in the prompt 
# are imported or defined here correctly inheriting from the Base above. 
# I will use the class names exactly as you provided.)
# ---------------------------------------------------------------

# RE-INSERTING NECESSARY MODEL IMPORTS/DEFINITIONS FOR THE SCRIPT TO WORK
# [Truncated: Assuming the models from the prompt are available in scope]
# ... (Include contents of amenities.py, property.py, etc. here if not importing) ...
# ---------------------------------------------------------------
# END MODEL SETUP

# Configure your database URL here

DATABASE_URL="postgresql+psycopg2://myuser:mypassword@localhost:5432/eygar_property_listing_db"
# For testing without Postgres, you can use SQLite:
# DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Configuration & Data Sources ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
fake = Faker()

# 1. Static Data: Amenities
AMENITIES_DATA = [
    # Basic
    {"name": "Wi-Fi", "category": "basic", "icon": "wifi"},
    {"name": "Air conditioning", "category": "basic", "icon": "snowflake"},
    {"name": "Heating", "category": "basic", "icon": "thermometer"},
    {"name": "Dedicated workspace", "category": "basic", "icon": "desk"},
    {"name": "Washer", "category": "basic", "icon": "washing-machine"},
    {"name": "Dryer", "category": "basic", "icon": "dryer"},
    # Kitchen
    {"name": "Kitchen", "category": "kitchen", "icon": "kitchen"},
    {"name": "Refrigerator", "category": "kitchen", "icon": "fridge"},
    {"name": "Microwave", "category": "kitchen", "icon": "microwave"},
    {"name": "Dishwasher", "category": "kitchen", "icon": "dishwasher"},
    {"name": "Coffee maker", "category": "kitchen", "icon": "coffee"},
    # Entertainment
    {"name": "TV", "category": "entertainment", "icon": "tv"},
    {"name": "Pool table", "category": "entertainment", "icon": "pool-8-ball"},
    # Accessibility
    {"name": "Step-free access", "category": "accessibility", "icon": "wheelchair"},
    {"name": "Wide doorways", "category": "accessibility", "icon": "door-open"},
]

# 2. Static Data: Safety Features
SAFETY_DATA = [
    {"name": "Smoke alarm", "description": "Fitted in all sleeping areas.", "icon": "sensor-smoke"},
    {"name": "Carbon monoxide alarm", "description": "Fitted near combustion appliances.", "icon": "sensor-on"},
    {"name": "Fire extinguisher", "description": "Easily accessible in the kitchen.", "icon": "fire-extinguisher"},
    {"name": "First aid kit", "description": "Available in the main bathroom cabinet.", "icon": "medical-bag"},
    {"name": "Lock on bedroom door", "description": "Private room can be locked.", "icon": "lock"},
]

# 3. Real-looking Image URLs (Using Unsplash Source for Demo)
# Categorized to match property types better
IMAGE_POOLS = {
    "modern_apt": [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502005229766-939cb6a50fe8?auto=format&fit=crop&w=800&q=80",
    ],
    "luxury_villa": [
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80",
    ],
    "cozy_house": [
        "https://images.unsplash.com/photo-1513584684374-8bab748fbf90?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80",
    ]
}

# 4. Location Areas
LOCATIONS_META = {
    "Doha": {
        "country": "Qatar",
        "currency": "QAR",
        "areas": ["The Pearl", "West Bay", "Msheireb Downtown", "Lusail", "Al Sadd"],
        "lat_range": (25.25, 25.40),
        "lon_range": (51.48, 51.55)
    },
    "Dubai": {
        "country": "United Arab Emirates",
        "currency": "AED",
        "areas": ["Dubai Marina", "Downtown Dubai", "Palm Jumeirah", "JBR", "Business Bay"],
        "lat_range": (25.06, 25.20),
        "lon_range": (55.13, 55.29)
    }
}

# --- Helper Functions ---

def get_or_create_amenities(db: Session):
    """Populates basic amenities and returns the objects."""
    logger.info("Seeding Amenities...")
    db_amenities = []
    for data in AMENITIES_DATA:
        amenity = db.query(Amenity).filter_by(name=data["name"]).first()
        if not amenity:
            amenity = Amenity(**data)
            db.add(amenity)
            db.commit() # Commit to get ID
            db.refresh(amenity)
        db_amenities.append(amenity)
    return db_amenities

def get_or_create_safety_features(db: Session):
    """Populates safety features and returns objects, identifying critical ones."""
    logger.info("Seeding Safety Features...")
    all_features = []
    critical_features = []
    critical_names = ["Smoke alarm", "Carbon monoxide alarm", "Fire extinguisher", "First aid kit"]
    
    for data in SAFETY_DATA:
        feature = db.query(SafetyFeature).filter_by(name=data["name"]).first()
        if not feature:
            feature = SafetyFeature(**data)
            db.add(feature)
            db.commit()
            db.refresh(feature)
        all_features.append(feature)
        if feature.name in critical_names:
            critical_features.append(feature)
            
    return all_features, critical_features

def generate_random_coordinate(lat_range, lon_range):
    lat = random.uniform(lat_range[0], lat_range[1])
    lon = random.uniform(lon_range[0], lon_range[1])
    return round(lat, 6), round(lon, 6)

def create_property_rules(db: Session, property_id: uuid.UUID):
    """Adds standard rules to a property."""
    rules = [
        {"text": "No smoking inside.", "type": "house_rules"},
        {"text": "No parties or events.", "type": "house_rules"},
        {"text": "Quiet hours after 10:00 PM.", "type": "house_rules"},
        {"text": "Free cancellation for 48 hours.", "type": "cancellation_policy"},
        {"text": "Check-in after 3:00 PM, Check-out before 11:00 AM.", "type": "check_in_policy"},
    ]
    for r in rules:
        rule_obj = PropertyRule(
            property_id=property_id,
            rule_text=r["text"],
            rule_type=r["type"]
        )
        db.add(rule_obj)

def add_property_images(db: Session, property_id: uuid.UUID, prop_type: str):
    """Adds relevant images to the property."""
    
    if prop_type in ["apartment", "hotel"]:
        pool = IMAGE_POOLS["modern_apt"]
    elif prop_type == "house" and random.random() > 0.5:
        pool = IMAGE_POOLS["luxury_villa"]
    else:
        pool = IMAGE_POOLS["cozy_house"]
        
    # Select a realistic number of images, from 3 up to the total available
    # THIS IS THE CORRECTED LINE:
    num_images = random.randint(min(3, len(pool)), len(pool))
    
    selected_urls = random.sample(pool, num_images)
    
    for i, url in enumerate(selected_urls):
        img = PropertyImage(
            property_id=property_id,
            image_url=url,
            display_order=i,
            is_cover=(i == 0),
            alt_text=f"View of the {prop_type}"
        )
        db.add(img)

# --- Main Seeding Function ---

def seed_database():
    # Ensure tables exist (Optional if using Alembic, but good for demo)
    # Base.metadata.drop_all(bind=engine) # Uncomment to reset DB
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Static Data
        amenities_list = get_or_create_amenities(db)
        safety_list, critical_safety = get_or_create_safety_features(db)
        
        logger.info("Starting Property Generation (Target: 50)...")
        
        # Setup distribution for Featured and Safety Badged
        total_props = 50
        indices = list(range(total_props))
        random.shuffle(indices)
        
        # First 10 are featured
        featured_indices = set(indices[:10])
        # Next 10 (overlapping possible if reshuffled, let's pick distinct for clarity or overlap for realism)
        # Let's just pick another random sample for safety to allow overlap
        safety_badged_indices = set(random.sample(range(total_props), 10))

        properties_created = 0
        
        for i in range(total_props):
            # Determine Flags
            is_featured = i in featured_indices
            # "Safety badged" implies they have all critical safety features verified
            is_safety_badged = i in safety_badged_indices
            
            # Determine Location (Split roughly 50/50 Doha/Dubai)
            city_key = "Doha" if i % 2 == 0 else "Dubai"
            loc_meta = LOCATIONS_META[city_key]
            area = random.choice(loc_meta["areas"])
            lat, lon = generate_random_coordinate(loc_meta["lat_range"], loc_meta["lon_range"])
            
            # Create Location
            location = Location(
                address=f"{fake.street_address()}, {area}",
                city=city_key,
                state=area, # Using area as state for context
                country=loc_meta["country"],
                postal_code=fake.postcode(),
                latitude=lat,
                longitude=lon
            )
            db.add(location)
            db.flush() # Get ID
            
            # Determine Property Details
            p_type = random.choice(["apartment", "house", "guest_house"])
            place_type = random.choice(["entire_place", "private_room"])
            
            # Make featured/safe ones look more premium (verified, entire place)
            if is_featured or is_safety_badged:
                verif_status = "verified"
                place_type = "entire_place"
            else:
                verif_status = random.choice(["verified", "pending"])

            # Generate logical capacities & price
            if place_type == "private_room":
                bedrooms = 1
                max_guests = 2
                price_base = random.randint(5000, 15000) # $50 - $150 (in cents)
            else:
                bedrooms = random.randint(1, 5)
                max_guests = bedrooms * 2 + random.randint(0, 2)
                price_base = random.randint(10000, 80000) * bedrooms # Scale by size
            
            # Adjust price for city/premium
            if city_key == "Dubai": price_base = int(price_base * 1.2)
            if is_featured: price_base = int(price_base * 1.5)

            adj_list = [fake.word().title() for _ in range(2)]
            title = f"{' '.join(adj_list)} {p_type.title().replace('_',' ')} in {area}"
            if is_featured:
                title = f"LUXURY: {title}"
                
            # Host Data (Denormalized)
            host_uuid = uuid.uuid4() # Mock auth ID
            host_fname = fake.first_name()
            
            # Create Property
            prop = Property(
                title=title,
                slug=fake.slug() + f"-{uuid.uuid4().hex[:6]}", # Ensure unique slug
                description=fake.paragraph(nb_sentences=5),
                property_type=p_type,
                place_type=place_type,
                bedrooms=bedrooms,
                beds=max_guests, # Simplification
                bathrooms=float(random.randint(1, bedrooms)),
                max_guests=max_guests,
                price_per_night=price_base,
                currency=loc_meta["currency"],
                cleaning_fee=random.randint(2000, 10000),
                location_id=location.id,
                is_active=True,
                is_featured=is_featured,
                verification_status=verif_status,
                instant_book=random.choice([True, False]),
                host_id=host_uuid,
                host_name=f"{host_fname} {fake.last_name()}",
                host_email=fake.email(),
                host_avatar=f"https://i.pravatar.cc/150?u={host_uuid}",
                published_at=datetime.now(UTC) - timedelta(days=random.randint(1, 300))
            )
            db.add(prop)
            db.flush() # Get ID for relationships
            
            # --- Link Relationships ---
            
            # 1. Images
            add_property_images(db, prop.id, p_type)
            
            # 2. Rules
            create_property_rules(db, prop.id)
            
            # 3. Amenities (Random selection of 5-10)
            prop.amenities = random.sample(amenities_list, random.randint(5, min(len(amenities_list), 12)))
            
            # 4. Safety Features
            if is_safety_badged:
                # Give them ALL critical ones + some others
                prop.safety_features = critical_safety + \
                    random.sample([sf for sf in safety_list if sf not in critical_safety], random.randint(0, 1))
                logger.debug(f"Prop {prop.id} is safety badged.")
            else:
                # Random selection
                prop.safety_features = random.sample(safety_list, random.randint(1, len(safety_list)-1))

            # 5. Fake Reviews (Optional, to populate ratings)
            num_reviews = random.randint(0, 15)
            total_score = 0
            if num_reviews > 0:
                for _ in range(num_reviews):
                    rating = random.randint(3, 5) if is_featured else random.randint(2, 5)
                    review = Review(
                        property_id=prop.id,
                        user_id=uuid.uuid4(), # Mock user
                        rating=rating,
                        comment=fake.sentence(),
                        cleanliness_rating=random.randint(3,5)
                    )
                    db.add(review)
                    total_score += rating
                # Update property aggregates
                prop.total_reviews = num_reviews
                prop.average_rating = round(total_score / num_reviews, 2)

            properties_created += 1
            if properties_created % 10 == 0:
                logger.info(f"Generated {properties_created}/50 properties...")

        db.commit()
        logger.info("Successfully populated database!")
        logger.info(f"Total: {properties_created}, Featured: 10, Safety Badged (Critical Features): 10 (approx, may overlap)")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Check if DB is configured (simple check for the default placeholder)
    if "user:password" in DATABASE_URL and "sqlite" not in DATABASE_URL:
        print("Please configure the DATABASE_URL in the script before running.")
    else:
        seed_database()