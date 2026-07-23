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

## 🔑 API Endpoints & Examples

All requests to endpoints that require authorization must include the header `Authorization: Bearer <JWT_TOKEN>`.

### 1. Properties

#### Create Property
* **Endpoint**: `POST /api/v1/properties/create`
* **Auth Required**: Yes (Host only)
* **Request Format**: Multipart Form Data
  * `property_data` (JSON string of `PropertyCreate` schema)
  * `image_files` (Optional, array of file uploads)
* **Request Body Example (`property_data` JSON)**:
```json
{
  "title": "Luxury Beachfront Villa with Infinity Pool - The Pearl, Qatar",
  "description": "Experience unparalleled luxury in this stunning 4-bedroom beachfront villa located in the prestigious Pearl-Qatar development in Doha. This exquisite property features an infinity pool overlooking the Arabian Gulf, private beach access, and breathtaking sea views. Perfect for families or groups seeking the ultimate luxury getaway in Qatar.",
  "property_type": "apartment",
  "place_type": "private_room",
  "bedrooms": 4,
  "beds": 5,
  "bathrooms": 3.5,
  "max_guests": 8,
  "max_adults": 8,
  "max_children": 4,
  "max_infants": 2,
  "pets_allowed": false,
  "price_per_night": 45000,
  "currency": "USD",
  "cleaning_fee": 15000,
  "service_fee": 5000,
  "weekly_discount": 10.0,
  "monthly_discount": 15.0,
  "instant_book": true,
  "location": {
    "address": "123 Porto Arabia Drive, The Pearl-Qatar",
    "city": "Doha",
    "state": "Ad Dawhah",
    "country": "Qatar",
    "postal_code": null,
    "latitude": 25.3725,
    "longitude": 51.554
  },
  "amenity_ids": [
    "6987ee35-d564-48ca-99cd-56fcb00db087",
    "703b97ec-ad39-4263-81b1-2251bdcd544b"
  ],
  "safety_feature_ids": [
    "77265249-193c-4911-896b-8bc621e67d0d"
  ],
  "images": [
    {
      "image_url": "https://example.com/images/property1-main.jpg",
      "display_order": 0,
      "is_cover": true,
      "alt_text": "Main sea view of the Arabian Gulf"
    },
    {
      "image_url": "https://example.com/images/property1-pool.jpg",
      "display_order": 1,
      "is_cover": false,
      "alt_text": "Infinity pool overlooking the sea"
    },
    {
      "image_url": "https://example.com/images/property1-bedroom.jpg",
      "display_order": 2,
      "is_cover": false,
      "alt_text": "Master bedroom with Arabian Gulf views"
    }
  ],
  "house_rules": [
    "No smoking inside the property",
    "No parties or events",
    "Respect local culture and traditions"
  ],
  "cancellation_policy": "Free cancellation up to 48 hours before check-in.",
  "check_in_policy": "Check-in: 3:00 PM - 10:00 PM. Concierge check-in or self check-in with keypad."
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Luxury Beachfront Villa with Infinity Pool",
  "slug": "luxury-beachfront-villa-with-infinity-pool",
  "description": "Experience paradise in this stunning 4-bedroom beachfront villa featuring an infinity pool...",
  "property_type": "entire_place",
  "place_type": "entire_home_apt",
  "bedrooms": 4,
  "beds": 5,
  "bathrooms": 3.5,
  "max_guests": 8,
  "max_adults": 8,
  "max_children": 4,
  "max_infants": 2,
  "pets_allowed": false,
  "price_per_night": 45000,
  "currency": "USD",
  "cleaning_fee": 15000,
  "service_fee": 5000,
  "weekly_discount": 10.0,
  "monthly_discount": 15.0,
  "instant_book": true,
  "host_id": "host-user-uuid",
  "host_name": "John Doe",
  "host_email": "john@example.com",
  "host_avatar": "https://example.com/avatar.jpg",
  "location": {
    "id": "location-uuid",
    "address": "123 Beachfront Drive",
    "city": "Miami Beach",
    "state": "Florida",
    "country": "USA",
    "postal_code": "33139",
    "latitude": 25.7907,
    "longitude": -80.13
  },
  "is_active": true,
  "is_featured": false,
  "verification_status": "pending",
  "average_rating": 0.0,
  "total_reviews": 0,
  "images": [
    {
      "id": "image-uuid",
      "property_id": "123e4567-e89b-12d3-a456-426614174000",
      "image_url": "https://example.com/images/property1-main.jpg",
      "display_order": 0,
      "is_cover": true,
      "alt_text": "Main ocean view",
      "uploaded_at": "2026-07-23T11:21:52Z"
    }
  ],
  "amenities": [],
  "created_at": "2026-07-23T11:21:52Z",
  "updated_at": "2026-07-23T11:21:52Z",
  "published_at": null
}
```

#### List Properties
* **Endpoint**: `GET /api/v1/properties/`
* **Auth Required**: No
* **Query Parameters**: `page` (default: 1), `page_size` (default: 20)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Luxury Beachfront Villa with Infinity Pool",
      "slug": "luxury-beachfront-villa-with-infinity-pool",
      "property_type": "entire_place",
      "place_type": "entire_home_apt",
      "price_per_night": 45000,
      "currency": "USD",
      "bedrooms": 4,
      "beds": 5,
      "bathrooms": 3.5,
      "max_guests": 8,
      "average_rating": 4.8,
      "total_reviews": 12,
      "is_featured": true,
      "host_id": "host-user-uuid",
      "host_name": "John Doe",
      "host_email": "john@example.com",
      "host_avatar": "https://example.com/avatar.jpg",
      "location": {
        "id": "location-uuid",
        "address": "123 Beachfront Drive",
        "city": "Miami Beach",
        "state": "Florida",
        "country": "USA",
        "postal_code": "33139",
        "latitude": 25.7907,
        "longitude": -80.13
      },
      "cover_image": "https://example.com/images/property1-main.jpg",
      "images": ["https://example.com/images/property1-main.jpg"],
      "experiences": []
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Search Properties
* **Endpoint**: `GET /api/v1/properties/search`
* **Auth Required**: No
* **Query Parameters**:
  * `location` (string)
  * `check_in` (string, YYYY-MM-DD)
  * `check_out` (string, YYYY-MM-DD)
  * `min_price` (integer)
  * `max_price` (integer)
  * `bedrooms` (integer)
  * `sort_by` (`price_asc`, `price_desc`, `rating`, `newest`)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Luxury Beachfront Villa with Infinity Pool",
      "slug": "luxury-beachfront-villa-with-infinity-pool",
      "property_type": "entire_place",
      "place_type": "entire_home_apt",
      "price_per_night": 45000,
      "currency": "USD",
      "bedrooms": 4,
      "beds": 5,
      "bathrooms": 3.5,
      "max_guests": 8,
      "average_rating": 4.8,
      "total_reviews": 12,
      "is_featured": true,
      "host_id": "host-user-uuid",
      "host_name": "John Doe",
      "host_email": "john@example.com",
      "host_avatar": "https://example.com/avatar.jpg",
      "location": {
        "id": "location-uuid",
        "address": "123 Beachfront Drive",
        "city": "Miami Beach",
        "state": "Florida",
        "country": "USA",
        "postal_code": "33139",
        "latitude": 25.7907,
        "longitude": -80.13
      },
      "cover_image": "https://example.com/images/property1-main.jpg",
      "images": ["https://example.com/images/property1-main.jpg"],
      "experiences": []
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Get Property Details
* **Endpoint**: `GET /api/v1/properties/{property_id}`
* **Auth Required**: No
* **Response Example (200 OK)**:
*(Returns full `PropertyResponse` schema as shown in property creation).*

#### Update Property
* **Endpoint**: `PUT /api/v1/properties/{property_id}`
* **Auth Required**: Yes (Property Owner only)
* **Request Body Example**:
```json
{
  "title": "Stunning Beachfront Villa with Infinity Pool",
  "price_per_night": 50000,
  "max_guests": 10
}
```
* **Response Example (200 OK)**:
*(Returns updated `PropertyResponse` schema).*

#### Partial Update Property
* **Endpoint**: `PATCH /api/v1/properties/{property_id}`
* **Auth Required**: Yes (Property Owner only)
* **Request Body Example**:
```json
{
  "price_per_night": 48000
}
```
* **Response Example (200 OK)**:
*(Returns updated `PropertyResponse` schema).*

#### Delete Property
* **Endpoint**: `DELETE /api/v1/properties/{property_id}`
* **Auth Required**: Yes (Property Owner only)
* **Response Example (200 OK)**:
```json
{
  "message": "Property deleted successfully"
}
```

#### Get Host's Properties
* **Endpoint**: `GET /api/v1/properties/host/{host_id}`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Luxury Beachfront Villa with Infinity Pool",
      "slug": "luxury-beachfront-villa-with-infinity-pool",
      "property_type": "entire_place",
      "place_type": "entire_home_apt",
      "price_per_night": 45000,
      "currency": "USD",
      "average_rating": 4.8,
      "total_reviews": 12,
      "is_featured": true,
      "host_id": "host-user-uuid",
      "host_name": "John Doe",
      "location": {
        "id": "location-uuid",
        "city": "Miami Beach",
        "country": "USA",
        "latitude": 25.7907,
        "longitude": -80.13
      }
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### 2. Reviews

#### Create Review
* **Endpoint**: `POST /api/v1/properties/{property_id}/reviews`
* **Auth Required**: Yes (Authenticated user, must not be property owner)
* **Request Body Example**:
```json
{
  "rating": 5,
  "comment": "Absolutely amazing property! Everything was exactly as described.",
  "cleanliness_rating": 5,
  "accuracy_rating": 5,
  "communication_rating": 5,
  "location_rating": 5,
  "check_in_rating": 5,
  "value_rating": 5
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "review-uuid-value",
  "property_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-uuid-value",
  "user_name": "Jane Smith",
  "user_avatar": "https://example.com/avatars/jane.jpg",
  "rating": 5,
  "comment": "Absolutely amazing property! Everything was exactly as described.",
  "cleanliness_rating": 5,
  "accuracy_rating": 5,
  "communication_rating": 5,
  "location_rating": 5,
  "check_in_rating": 5,
  "value_rating": 5,
  "helpful_count": 0,
  "created_at": "2026-07-23T11:21:52Z",
  "updated_at": "2026-07-23T11:21:52Z"
}
```

#### List Property Reviews
* **Endpoint**: `GET /api/v1/properties/{property_id}/reviews`
* **Auth Required**: No
* **Query Parameters**: `page` (default: 1), `page_size` (default: 10)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "review-uuid-value",
      "property_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "user-uuid-value",
      "user_name": "Jane Smith",
      "rating": 5,
      "comment": "Absolutely amazing property!",
      "helpful_count": 0,
      "created_at": "2026-07-23T11:21:52Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

#### Update Review
* **Endpoint**: `PUT /api/v1/reviews/{review_id}`
* **Auth Required**: Yes (Review author only)
* **Request Body Example**:
```json
{
  "rating": 4,
  "comment": "Updated: Great property, minor issue with check-in process."
}
```
* **Response Example (200 OK)**:
*(Returns updated `ReviewResponse` details).*

#### Delete Review
* **Endpoint**: `DELETE /api/v1/reviews/{review_id}`
* **Auth Required**: Yes (Review author only)
* **Response Example (200 OK)**:
```json
{
  "message": "Review deleted successfully"
}
```

#### Mark Review Helpful
* **Endpoint**: `POST /api/v1/reviews/{review_id}/helpful`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
{
  "id": "review-uuid-value",
  "helpful_count": 1
}
```

---

### 3. Amenities & Safety Features

#### List All Amenities
* **Endpoint**: `GET /api/v1/amenities`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "WiFi",
    "category": "Basic",
    "icon": "wifi-icon-name"
  }
]
```

#### Create Amenity
* **Endpoint**: `POST /api/v1/amenities`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "name": "Swimming Pool",
  "category": "basic",
  "icon": "pool-icon"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Swimming Pool",
  "category": "basic",
  "icon": "pool-icon"
}
```

#### List All Safety Features
* **Endpoint**: `GET /api/v1/safety-features`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Smoke Alarm",
    "icon": "smoke-alarm-icon"
  }
]
```

#### Create Safety Feature
* **Endpoint**: `POST /api/v1/safety-features`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "name": "Fire Extinguisher",
  "description": "Portable fire extinguisher located in the kitchen",
  "icon": "fire-extinguisher-icon"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Fire Extinguisher",
  "description": "Portable fire extinguisher located in the kitchen",
  "icon": "fire-extinguisher-icon"
}
```

---

### 4. Categories

#### Create Category
* **Endpoint**: `POST /api/v1/categories/`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "name": "Beachfront",
  "slug": "beachfront",
  "description": "Properties located right next to the beach",
  "icon": "beach-icon-url",
  "is_active": true
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Beachfront",
  "slug": "beachfront",
  "description": "Properties located right next to the beach",
  "icon": "beach-icon-url",
  "is_active": true,
  "created_at": "2026-07-23T11:21:52Z",
  "updated_at": "2026-07-23T11:21:52Z"
}
```

#### List Categories
* **Endpoint**: `GET /api/v1/categories/`
* **Auth Required**: No
* **Query Parameters**: `skip` (default: 0), `limit` (default: 100)
* **Response Example (200 OK)**:
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Beachfront",
    "slug": "beachfront",
    "description": "Properties located right next to the beach",
    "icon": "beach-icon-url",
    "is_active": true,
    "created_at": "2026-07-23T11:21:52Z",
    "updated_at": "2026-07-23T11:21:52Z"
  }
]
```

#### Delete Category
* **Endpoint**: `DELETE /api/v1/categories/{category_id}`
* **Auth Required**: Yes
* **Response Example (204 No Content)**:
*(No content returned)*

---

### 5. User Properties

#### Get Authenticated User's Properties
* **Endpoints**: 
  * `GET /api/v1/my-properties`
  * `GET /api/v1/properties/my`
* **Auth Required**: Yes (Host profile required)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Luxury Beachfront Villa with Infinity Pool",
      "slug": "luxury-beachfront-villa-with-infinity-pool",
      "property_type": "entire_place",
      "place_type": "entire_home_apt",
      "price_per_night": 45000,
      "currency": "USD",
      "bedrooms": 4,
      "beds": 5,
      "bathrooms": 3.5,
      "max_guests": 8,
      "average_rating": 4.8,
      "total_reviews": 12,
      "is_featured": true,
      "host_id": "host-user-uuid",
      "host_name": "John Doe",
      "location": {
        "id": "location-uuid",
        "city": "Miami Beach",
        "country": "USA"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### 6. Experiences

#### Create Experience
* **Endpoint**: `POST /api/v1/experiences/`
* **Auth Required**: Yes (Host only)
* **Request Body Example**:
```json
{
  "title": "Sunset Sailing Tour",
  "description": "A wonderful sailing trip into the ocean during sunset hours.",
  "image_url": "https://example.com/sailing.jpg",
  "min_nights": 2,
  "property_ids": ["123e4567-e89b-12d3-a456-426614174000"]
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "experience-uuid-value",
  "title": "Sunset Sailing Tour",
  "description": "A wonderful sailing trip into the ocean during sunset hours.",
  "image_url": "https://example.com/sailing.jpg",
  "min_nights": 2,
  "host_id": "host-user-uuid",
  "is_active": true,
  "created_at": "2026-07-23T11:21:52Z",
  "updated_at": "2026-07-23T11:21:52Z"
}
```

#### List Host's Experiences
* **Endpoint**: `GET /api/v1/experiences/my-experiences`
* **Auth Required**: Yes (Host only)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "experience-uuid-value",
      "title": "Sunset Sailing Tour",
      "description": "A wonderful sailing trip into the ocean during sunset hours.",
      "image_url": "https://example.com/sailing.jpg",
      "min_nights": 2,
      "host_id": "host-user-uuid",
      "is_active": true,
      "created_at": "2026-07-23T11:21:52Z",
      "updated_at": "2026-07-23T11:21:52Z",
      "property_count": 1,
      "properties": [
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "title": "Luxury Beachfront Villa with Infinity Pool"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Get Experience by ID
* **Endpoint**: `GET /api/v1/experiences/{experience_id}`
* **Auth Required**: No
* **Response Example (200 OK)**:
*(Returns a single experience detail including property list, similar to above).*

#### Update Experience
* **Endpoint**: `PUT /api/v1/experiences/{experience_id}`
* **Auth Required**: Yes (Host owner only)
* **Request Body Example**:
```json
{
  "title": "Private Sunset Yacht Tour",
  "min_nights": 3
}
```
* **Response Example (200 OK)**:
*(Returns updated basic `ExperienceResponse` schema).*

#### Delete Experience
* **Endpoint**: `DELETE /api/v1/experiences/{experience_id}`
* **Auth Required**: Yes (Host owner only)
* **Response Example (200 OK)**:
```json
{
  "message": "Experience deleted successfully"
}
```

#### Get Experiences for a Property
* **Endpoint**: `GET /api/v1/experiences/property/{property_id}/experiences`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
[
  {
    "id": "experience-uuid-value",
    "title": "Sunset Sailing Tour",
    "description": "A wonderful sailing trip...",
    "image_url": "https://example.com/sailing.jpg",
    "min_nights": 2,
    "host_id": "host-user-uuid",
    "is_active": true,
    "created_at": "2026-07-23T11:21:52Z",
    "updated_at": "2026-07-23T11:21:52Z"
  }
]
```

#### List All Experiences
* **Endpoint**: `GET /api/v1/experiences/`
* **Auth Required**: No
* **Query Parameters**: `host_id` (Optional filter), `active_only` (default: true)
* **Response Example (200 OK)**:
```json
{
  "items": [
    {
      "id": "experience-uuid-value",
      "title": "Sunset Sailing Tour",
      "image_url": "https://example.com/sailing.jpg",
      "min_nights": 2,
      "host_id": "host-user-uuid",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### Attach Properties to Experience
* **Endpoint**: `POST /api/v1/experiences/{experience_id}/properties`
* **Auth Required**: Yes (Host owner only)
* **Request Body Example**:
```json
[
  "123e4567-e89b-12d3-a456-426614174000"
]
```
* **Response Example (200 OK)**:
*(Returns updated basic `ExperienceResponse` schema).*

#### Retrieve Properties for Experience
* **Endpoint**: `GET /api/v1/experiences/{experience_id}/properties`
* **Auth Required**: Yes (Host owner only)
* **Response Example (200 OK)**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Luxury Beachfront Villa with Infinity Pool",
    "slug": "luxury-beachfront-villa-with-infinity-pool",
    "property_type": "entire_place"
  }
]
```

#### Detach Property from Experience
* **Endpoint**: `DELETE /api/v1/experiences/{experience_id}/properties/{property_id}`
* **Auth Required**: Yes (Host owner only)
* **Response Example (200 OK)**:
```json
{
  "message": "Property removed from experience successfully"
}
```

---

### 7. Images

#### Upload Single Image
* **Endpoint**: `POST /api/v1/images/upload`
* **Auth Required**: Yes
* **Request Format**: Multipart Form Data
  * `image` (File payload)
  * `display_order` (Form integer, default: 0)
  * `is_cover` (Form boolean, default: false)
  * `alt_text` (Form string, default: "")
* **Response Example (200 OK)**:
```json
{
  "image_url": "http://localhost:8001/uploaded_images/properties/filename.jpg",
  "filename": "filename.jpg",
  "display_order": 0,
  "is_cover": false,
  "alt_text": "filename.jpg",
  "message": "Image uploaded successfully"
}
```

#### Upload Multiple Images
* **Endpoint**: `POST /api/v1/images/upload-multiple`
* **Auth Required**: Yes
* **Request Format**: Multipart Form Data
  * `images` (List of files)
* **Response Example (200 OK)**:
```json
{
  "message": "Successfully uploaded 2 images",
  "images": [
    {
      "image_url": "http://localhost:8001/uploaded_images/properties/1.jpg",
      "filename": "1.jpg",
      "display_order": 0,
      "is_cover": true,
      "alt_text": "1.jpg"
    },
    {
      "image_url": "http://localhost:8001/uploaded_images/properties/2.jpg",
      "filename": "2.jpg",
      "display_order": 1,
      "is_cover": false,
      "alt_text": "2.jpg"
    }
  ]
}
```

#### Delete Image
* **Endpoint**: `DELETE /api/v1/images/delete`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "image_url": "http://localhost:8001/uploaded_images/properties/filename.jpg"
}
```
* **Response Example (200 OK)**:
```json
{
  "message": "Image deleted successfully"
}
```

#### Health Check (Images Service)
* **Endpoint**: `GET /api/v1/images/health`
* **Auth Required**: No
* **Response Example (200 OK)**:
```json
{
  "status": "healthy",
  "environment": "development",
  "storage": "local"
}
```

---

### 8. Vendor Services

#### List Services
* **Endpoint**: `GET /api/v1/vendors/services`
* **Auth Required**: No
* **Query Parameters**: `page` (default: 1), `page_size` (default: 20)
* **Response Example (200 OK)**:
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "vendorId": "vendor-uuid-value",
    "vendorName": "Adventure Co.",
    "title": "Professional Dance Class",
    "description": "A fun and energetic dance class for all levels.",
    "category": "Training",
    "duration": 2,
    "allowedGuests": 10,
    "price": 100.0,
    "serviceArea": {
      "name": "Central Park",
      "lat": 40.785091,
      "lng": -73.968285,
      "radius": 5
    },
    "image": "https://example.com/image.jpg",
    "isActive": true,
    "rating": 4.5,
    "reviewCount": 8,
    "createdAt": "2026-07-23T11:21:52Z"
  }
]
```

#### List My Services
* **Endpoint**: `GET /api/v1/vendors/services/my`
* **Auth Required**: Yes
* **Response Example (200 OK)**:
*(Returns array of `VendorServiceResponse` belonging to logged-in user).*

#### List Services by Vendor
* **Endpoint**: `GET /api/v1/vendors/{vendor_id}/services`
* **Auth Required**: No
* **Response Example (200 OK)**:
*(Returns array of `VendorServiceResponse` belonging to requested vendor).*

#### Get Single Service
* **Endpoint**: `GET /api/v1/vendors/services/{service_id}`
* **Auth Required**: No
* **Response Example (200 OK)**:
*(Returns single `VendorServiceResponse` object).*

#### Add Service
* **Endpoint**: `POST /api/v1/vendors/services`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "title": "Professional Dance Class",
  "description": "A fun and energetic dance class for all levels.",
  "category": "Training",
  "duration": 2,
  "allowedGuests": 10,
  "price": 100.0,
  "serviceArea": {
    "name": "Central Park",
    "lat": 40.785091,
    "lng": -73.968285,
    "radius": 5
  },
  "image": "https://example.com/image.jpg",
  "isActive": true
}
```
* **Response Example (201 Created)**:
*(Returns created `VendorServiceResponse` object).*

#### Edit Service
* **Endpoint**: `PUT /api/v1/vendors/services/{service_id}`
* **Auth Required**: Yes (Service Owner only)
* **Request Body Example**:
```json
{
  "price": 120.0,
  "allowedGuests": 12
}
```
* **Response Example (200 OK)**:
*(Returns updated `VendorServiceResponse` object).*

#### Delete Service
* **Endpoint**: `DELETE /api/v1/vendors/services/{service_id}`
* **Auth Required**: Yes (Service Owner only)
* **Response Example (204 No Content)**:
*(No content returned)*

---

### 9. Vendor Coupons

#### Create Coupon
* **Endpoint**: `POST /api/v1/vendors/coupons`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "serviceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Summer Discount Coupon",
  "discountType": "percentage",
  "discountValue": 15.0,
  "validFrom": "2026-07-23T11:21:52Z",
  "validTo": "2026-08-23T11:21:52Z",
  "usageLimit": 100,
  "eligibility": "All Users",
  "terms": "Valid only during weekdays",
  "isActive": true,
  "code": "SUMMER15"
}
```
* **Response Example (201 Created)**:
```json
{
  "id": "coupon-uuid-value",
  "serviceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Summer Discount Coupon",
  "discountType": "percentage",
  "discountValue": 15.0,
  "validFrom": "2026-07-23T11:21:52Z",
  "validTo": "2026-08-23T11:21:52Z",
  "usageLimit": 100,
  "eligibility": "All Users",
  "terms": "Valid only during weekdays",
  "isActive": true,
  "code": "SUMMER15",
  "usedCount": 0,
  "createdAt": "2026-07-23T11:21:52Z"
}
```

#### List Coupons
* **Endpoint**: `GET /api/v1/vendors/coupons`
* **Auth Required**: No
* **Query Parameters**: `skip` (default: 0), `limit` (default: 100)
* **Response Example (200 OK)**:
```json
[
  {
    "id": "coupon-uuid-value",
    "serviceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "Summer Discount Coupon",
    "discountType": "percentage",
    "discountValue": 15.0,
    "validFrom": "2026-07-23T11:21:52Z",
    "validTo": "2026-08-23T11:21:52Z",
    "usageLimit": 100,
    "eligibility": "All Users",
    "terms": "Valid only during weekdays",
    "isActive": true,
    "code": "SUMMER15",
    "usedCount": 0,
    "createdAt": "2026-07-23T11:21:52Z",
    "service": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "vendorId": "vendor-uuid-value",
      "vendorName": "Adventure Co.",
      "title": "Professional Dance Class",
      "description": "A fun and energetic dance class for all levels.",
      "category": "Training",
      "duration": 2,
      "allowedGuests": 10,
      "price": 100.0,
      "image": "https://example.com/image.jpg",
      "isActive": true,
      "rating": 4.5,
      "reviewCount": 8,
      "createdAt": "2026-07-23T11:21:52Z"
    }
  }
]
```

#### Get Specific Coupon
* **Endpoint**: `GET /api/v1/vendors/coupons/{coupon_id}`
* **Auth Required**: No
* **Response Example (200 OK)**:
*(Returns single basic `Coupon` object).*

#### Update Coupon
* **Endpoint**: `PUT /api/v1/vendors/coupons/{coupon_id}`
* **Auth Required**: Yes
* **Request Body Example**:
```json
{
  "title": "Updated Summer Coupon",
  "discountValue": 20.0
}
```
* **Response Example (200 OK)**:
*(Returns updated `Coupon` object).*

#### Delete Coupon
* **Endpoint**: `DELETE /api/v1/vendors/coupons/{coupon_id}`
* **Auth Required**: Yes
* **Response Example (204 No Content)**:
*(No content returned)*

---

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
