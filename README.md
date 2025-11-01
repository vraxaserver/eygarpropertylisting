# Property Listing Microservice

A production-ready FastAPI microservice for managing property listings in a rental marketplace platform (similar to Airbnb).

## 🏗️ Architecture

- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT integration with Django REST auth service
- **Frontend**: Next.js (localhost:3000)
- **Auth Service**: Django REST (localhost:8000)
- **This Service**: FastAPI (localhost:8001)

## ✨ Features

- **Property Management**: Full CRUD operations for property listings
- **Advanced Search**: Filter by location, price, amenities, dates, and more
- **Reviews & Ratings**: User reviews with detailed rating categories
- **Amenities & Safety**: Categorized amenities and safety features
- **Image Management**: Multiple images per property with cover image support
- **Location-based Search**: Find properties near specific coordinates
- **Role-based Access**: Owner-only operations with JWT authentication
- **Comprehensive API**: RESTful endpoints with auto-generated documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)
- Auth service running on localhost:8000

### Installation

1. **Clone and setup**:
```bash
cd listing-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start PostgreSQL**:
```bash
docker-compose up -d postgres
```

4. **Run migrations**:
```bash
alembic revision --autogenerate -m "describe your change"
alembic revision --autogenerate -m "Add coupons table"

alembic upgrade head
```

5. **Seed database (optional)**:
```bash
python scripts/seed_data.py
```

6. **Start the service**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 🔑 API Endpoints

### Properties

```
POST   /api/v1/properties/              Create property (auth required)
GET    /api/v1/properties/              List all properties
GET    /api/v1/properties/search        Advanced search with filters
GET    /api/v1/properties/featured      Get featured properties
GET    /api/v1/properties/nearby        Search by coordinates
GET    /api/v1/properties/{id}          Get property details
PUT    /api/v1/properties/{id}          Update property (owner only)
PATCH  /api/v1/properties/{id}          Partial update (owner only)
DELETE /api/v1/properties/{id}          Delete property (owner only)
GET    /api/v1/properties/host/{id}     Get host's properties
```

### Reviews

```
POST   /api/v1/properties/{id}/reviews  Create review (auth required)
GET    /api/v1/properties/{id}/reviews  List property reviews
PUT    /api/v1/reviews/{id}             Update review (author only)
DELETE /api/v1/reviews/{id}             Delete review (author only)
POST   /api/v1/reviews/{id}/helpful     Mark review helpful
```

### Amenities & Features

```
GET    /api/v1/amenities                List all amenities
GET    /api/v1/safety-features          List all safety features
```

### User Properties

```
GET    /api/v1/my-properties            Get authenticated user's properties
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_properties.py -v

# Run with markers
pytest -m "asyncio"
```

Test coverage target: **85%+**

## 🗄️ Database Models

### Core Models

- **Property**: Main listing with pricing, capacity, location
- **Location**: Geographic information with coordinates
- **PropertyImage**: Multiple images with display order
- **Amenity**: Categorized amenities (WiFi, Kitchen, etc.)
- **SafetyFeature**: Safety equipment and certifications
- **Availability**: Date ranges for booking availability
- **PropertyRule**: House rules, policies, check-in info
- **Review**: User reviews with detailed ratings

### Relationships

- Property ↔ Location (One-to-One)
- Property ↔ Images (One-to-Many)
- Property ↔ Amenities (Many-to-Many)
- Property ↔ SafetyFeatures (Many-to-Many)
- Property ↔ Reviews (One-to-Many)
- Property ↔ Availabilities (One-to-Many)
- Property ↔ Rules (One-to-Many)

## 🔐 Authentication

This service integrates with an external Django REST auth service:

```python
# Auth flow
1. User authenticates with auth service (localhost:8000)
2. Receives JWT token
3. Includes token in requests: Authorization: Bearer <token>
4. This service validates token with auth service
5. Extracts user info and enforces permissions
```

**Protected Endpoints**: Require valid JWT token
**Owner-Only Operations**: Additional check that user owns the resource

## 📦 Project Structure

```
listing-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── database.py             # DB connection
│   ├── dependencies.py         # Auth & pagination
│   ├── models/                 # SQLAlchemy models
│   │   ├── property.py
│   │   ├── image.py
│   │   ├── amenity.py
│   │   ├── availability.py
│   │   ├── rule.py
│   │   └── review.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── property.py
│   │   ├── review.py
│   │   ├── amenity.py
│   │   └── common.py
│   ├── api/v1/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── properties.py
│   │       ├── reviews.py
│   │       ├── amenities.py
│   │       └── my_properties.py
│   ├── services/               # Business logic
│   │   ├── property_service.py
│   │   └── review_service.py
│   └── repositories/           # Data access
│       ├── property_repository.py
│       └── review_repository.py
├── tests/
│   ├── conftest.py
│   ├── test_properties.py
│   └── test_reviews.py
├── alembic/                    # Migrations
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🌍 Environment Variables

Key configuration variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/listing_db

# Auth Service
AUTH_SERVICE_URL=http://127.0.0.1:8000
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Server
HOST=0.0.0.0
PORT=8001
DEBUG=True
```

## 🔍 Search & Filtering

The service supports advanced filtering:

```python
# Example: Search properties
GET /api/v1/properties/search?
    location=Miami&
    check_in=2025-01-01&
    check_out=2025-01-07&
    adults=2&
    children=1&
    min_price=10000&
    max_price=30000&
    bedrooms=2&
    property_type=entire_place&
    instant_book=true&
    sort_by=price_asc
```

## 📊 Business Rules

- Minimum 3 images required per property
- Users cannot review their own properties
- One review per user per property
- Property ratings automatically calculated from reviews
- Only owners can modify their properties
- Inactive properties hidden from public listings

## 🚢 Deployment

### Docker Deployment

```bash
# Build image
docker build -t listing-service:latest .

# Run container
docker run -d \
  --name listing-service \
  -p 8001:8001 \
  --env-file .env \
  listing-service:latest
```

### Production Considerations

- Use production-grade ASGI server (Gunicorn + Uvicorn)
- Enable SSL/TLS
- Configure proper CORS origins
- Set up monitoring and logging
- Use environment-specific secrets
- Implement rate limiting
- Set up database backups
- Configure Redis for caching

## 🤝 Integration with Other Services

### Auth Service (Django REST)

```python
# Endpoint: GET http://127.0.0.1:8000/api/auth/me/
# Headers: Authorization: Bearer <token>
# Returns: User profile data
```

### Future Services

- **Booking Service**: Check availability, create reservations
- **Payment Service**: Process payments and payouts
- **Messaging Service**: Host-guest communication
- **Notification Service**: Email/SMS notifications

## 📝 API Examples

### Create Property

```bash
curl -X POST http://localhost:8001/api/v1/properties/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Luxury Beach Villa",
    "description": "Beautiful beachfront property...",
    "property_type": "entire_place",
    "bedrooms": 3,
    "beds": 4,
    "bathrooms": 2.5,
    "max_guests": 6,
    "price_per_night": 25000,
    "currency": "USD",
    "location": {
      "address": "123 Beach Rd",
      "city": "Miami",
      "country": "USA",
      "latitude": 25.7617,
      "longitude": -80.1918
    },
    "images": [...],
    "amenity_ids": [...],
    "house_rules": [...]
  }'
```

### Search Properties

```bash
curl "http://localhost:8001/api/v1/properties/search?\
location=Miami&\
min_price=10000&\
max_price=30000&\
bedrooms=2&\
sort_by=price_asc"
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**:
```bash
# Check PostgreSQL is running
docker-compose ps

# Verify DATABASE_URL in .env
```

**Auth Service Unavailable**:
```bash
# Ensure auth service is running on localhost:8000
curl http://localhost:8000/api/auth/me/
```

**Migration Issues**:
```bash
# Reset database (DEV ONLY)
alembic downgrade base
alembic upgrade head
```

## 📄 License

MIT License - see LICENSE file for details

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at /docs
- Review test files for usage examples
