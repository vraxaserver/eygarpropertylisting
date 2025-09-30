import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
from uuid import uuid4
from faker import Faker

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models.property import Property, Location, PropertyType, VerificationStatus
from app.models.amenity import Amenity, AmenityCategory, SafetyFeature
from app.schemas.common import UserInfo

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://listing_user:listing_password@localhost:5433/listing_test_db"

fake = Faker()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user() -> UserInfo:
    """Create a test user."""
    return UserInfo(
        id=uuid4(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def another_user() -> UserInfo:
    """Create another test user."""
    return UserInfo(
        id=uuid4(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        is_active=True,
        is_verified=True
    )


@pytest.fixture
async def test_location(db_session: AsyncSession) -> Location:
    """Create a test location."""
    location = Location(
        address=fake.street_address(),
        city=fake.city(),
        state=fake.state(),
        country=fake.country(),
        postal_code=fake.postcode(),
        latitude=float(fake.latitude()),
        longitude=float(fake.longitude())
    )
    db_session.add(location)
    await db_session.commit()
    await db_session.refresh(location)
    return location


@pytest.fixture
async def test_property(db_session: AsyncSession, test_user: UserInfo, test_location: Location) -> Property:
    """Create a test property."""
    property_obj = Property(
        title=fake.sentence(nb_words=6),
        slug=fake.slug(),
        description=fake.text(max_nb_chars=500),
        property_type=PropertyType.ENTIRE_PLACE,
        bedrooms=2,
        beds=2,
        bathrooms=1.5,
        max_guests=4,
        max_adults=4,
        max_children=2,
        max_infants=1,
        pets_allowed=False,
        price_per_night=15000,  # $150.00
        currency="USD",
        cleaning_fee=5000,
        service_fee=2000,
        location_id=test_location.id,
        user_id=test_user.id,
        is_active=True,
        verification_status=VerificationStatus.VERIFIED,
        instant_book=True
    )
    db_session.add(property_obj)
    await db_session.commit()
    await db_session.refresh(property_obj)
    return property_obj


@pytest.fixture
async def test_amenities(db_session: AsyncSession) -> list[Amenity]:
    """Create test amenities."""
    amenities = [
        Amenity(name="WiFi", category=AmenityCategory.BASIC, icon="wifi"),
        Amenity(name="Kitchen", category=AmenityCategory.KITCHEN, icon="kitchen"),
        Amenity(name="TV", category=AmenityCategory.ENTERTAINMENT, icon="tv"),
        Amenity(name="Air Conditioning", category=AmenityCategory.BASIC, icon="ac"),
    ]
    for amenity in amenities:
        db_session.add(amenity)
    await db_session.commit()
    for amenity in amenities:
        await db_session.refresh(amenity)
    return amenities


@pytest.fixture
async def test_safety_features(db_session: AsyncSession) -> list[SafetyFeature]:
    """Create test safety features."""
    features = [
        SafetyFeature(name="Smoke Alarm", description="Working smoke alarm", icon="smoke"),
        SafetyFeature(name="Carbon Monoxide Alarm", description="Working CO alarm", icon="co"),
        SafetyFeature(name="First Aid Kit", description="Basic first aid kit", icon="medical"),
    ]
    for feature in features:
        db_session.add(feature)
    await db_session.commit()
    for feature in features:
        await db_session.refresh(feature)
    return features


def create_auth_header(user: UserInfo) -> dict:
    """Create authorization header for test user."""
    # In real tests, you'd generate a real JWT token
    # For simplicity, we're mocking the auth
    return {"Authorization": f"Bearer test_token_{user.id}"}