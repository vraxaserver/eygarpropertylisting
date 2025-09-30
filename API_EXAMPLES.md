# API Examples & Usage Guide

Complete guide with cURL examples for all endpoints in the Property Listing Microservice.

## Authentication

All protected endpoints require a JWT token from the auth service:

```bash
# Get token from auth service (example)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access')
```

## Property Endpoints

### 1. Create Property

```bash
curl -X POST http://localhost:8001/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Luxury Beachfront Villa with Infinity Pool",
    "description": "Experience paradise in this stunning 4-bedroom beachfront villa featuring an infinity pool, private beach access, and breathtaking ocean views. Perfect for families or groups seeking the ultimate luxury getaway.",
    "property_type": "entire_place",
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
    "weekly_discount": 10,
    "monthly_discount": 15,
    "instant_book": true,
    "location": {
      "address": "123 Beachfront Drive",
      "city": "Miami Beach",
      "state": "Florida",
      "country": "USA",
      "postal_code": "33139",
      "latitude": 25.7907,
      "longitude": -80.1300
    },
    "amenity_ids": [
      "uuid-of-wifi",
      "uuid-of-pool",
      "uuid-of-ac"
    ],
    "safety_feature_ids": [
      "uuid-of-smoke-alarm",
      "uuid-of-co-alarm"
    ],
    "images": [
      {
        "image_url": "https://example.com/images/property1-main.jpg",
        "display_order": 0,
        "is_cover": true,
        "alt_text": "Main ocean view"
      },
      {
        "image_url": "https://example.com/images/property1-pool.jpg",
        "display_order": 1,
        "is_cover": false,
        "alt_text": "Infinity pool"
      },
      {
        "image_url": "https://example.com/images/property1-bedroom.jpg",
        "display_order": 2,
        "is_cover": false,
        "alt_text": "Master bedroom"
      }
    ],
    "house_rules": [
      "No smoking inside the property",
      "No parties or events",
      "Quiet hours: 10 PM - 8 AM",
      "Please remove shoes indoors"
    ],
    "cancellation_policy": "Free cancellation up to 48 hours before check-in. After that, 50% refund up to 24 hours before check-in.",
    "check_in_policy": "Check-in: 3:00 PM - 10:00 PM. Self check-in with keypad. Code will be sent 24 hours before arrival."
  }'
```

### 2. List All Properties

```bash
curl http://localhost:8001/api/v1/properties/ \
  -G \
  --data-urlencode "page=1" \
  --data-urlencode "page_size=20"
```

### 3. Get Property by ID

```bash
PROPERTY_ID="your-property-uuid"
curl http://localhost:8001/api/v1/properties/$PROPERTY_ID
```

### 4. Search Properties

```bash
curl http://localhost:8001/api/v1/properties/search \
  -G \
  --data-urlencode "location=Miami" \
  --data-urlencode "check_in=2025-01-15" \
  --data-urlencode "check_out=2025-01-22" \
  --data-urlencode "adults=2" \
  --data-urlencode "children=1" \
  --data-urlencode "min_price=10000" \
  --data-urlencode "max_price=50000" \
  --data-urlencode "bedrooms=2" \
  --data-urlencode "property_type=entire_place" \
  --data-urlencode "instant_book=true" \
  --data-urlencode "sort_by=price_asc"
```

### 5. Get Featured Properties

```bash
curl http://localhost:8001/api/v1/properties/featured?limit=10
```

### 6. Search Nearby Properties

```bash
curl http://localhost:8001/api/v1/properties/nearby \
  -G \
  --data-urlencode "lat=25.7617" \
  --data-urlencode "lng=-80.1918" \
  --data-urlencode "radius=10" \
  --data-urlencode "limit=20"
```

### 7. Update Property

```bash
PROPERTY_ID="your-property-uuid"
curl -X PUT http://localhost:8001/api/v1/properties/$PROPERTY_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Luxury Villa",
    "price_per_night": 50000,
    "bedrooms": 5,
    "is_active": true
  }'
```

### 8. Partial Update Property

```bash
PROPERTY_ID="your-property-uuid"
curl -X PATCH http://localhost:8001/api/v1/properties/$PROPERTY_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_night": 48000
  }'
```

### 9. Delete Property

```bash
PROPERTY_ID="your-property-uuid"
curl -X DELETE http://localhost:8001/api/v1/properties/$PROPERTY_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 10. Get Host's Properties

```bash
HOST_ID="host-user-uuid"
curl http://localhost:8001/api/v1/properties/host/$HOST_ID
```

### 11. Get My Properties

```bash
curl http://localhost:8001/api/v1/my-properties \
  -H "Authorization: Bearer $TOKEN"
```

## Review Endpoints

### 1. Create Review

```bash
PROPERTY_ID="property-uuid"
curl -X POST http://localhost:8001/api/v1/properties/$PROPERTY_ID/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Absolutely amazing property! Everything was exactly as described. The host was very responsive and helpful. The location is perfect and the amenities are top-notch. Would definitely stay here again!",
    "cleanliness_rating": 5,
    "accuracy_rating": 5,
    "communication_rating": 5,
    "location_rating": 5,
    "check_in_rating": 5,
    "value_rating": 5
  }'
```

### 2. List Property Reviews

```bash
PROPERTY_ID="property-uuid"
curl http://localhost:8001/api/v1/properties/$PROPERTY_ID/reviews \
  -G \
  --data-urlencode "page=1" \
  --data-urlencode "page_size=10"
```

### 3. Update Review

```bash
REVIEW_ID="review-uuid"
curl -X PUT http://localhost:8001/api/v1/reviews/$REVIEW_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comment": "Updated review: Great property, minor issue with AC but host resolved it quickly."
  }'
```

### 4. Delete Review

```bash
REVIEW_ID="review-uuid"
curl -X DELETE http://localhost:8001/api/v1/reviews/$REVIEW_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Mark Review Helpful

```bash
REVIEW_ID="review-uuid"
curl -X POST http://localhost:8001/api/v1/reviews/$REVIEW_ID/helpful
```

## Amenity Endpoints

### 1. List All Amenities

```bash
curl http://localhost:8001/api/v1/amenities
```

### 2. List All Safety Features

```bash
curl http://localhost:8001/api/v1/safety-features
```

## Health Check

```bash
curl http://localhost:8001/health
```

## Response Examples

### Successful Property Creation (201)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Luxury Beachfront Villa",
  "slug": "luxury-beachfront-villa",
  "description": "Experience paradise...",
  "property_type": "entire_place",
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
  "weekly_discount": 10,
  "monthly_discount": 15,
  "user_id": "user-uuid",
  "location": {
    "id": "location-uuid",
    "address": "123 Beachfront Drive",
    "city": "Miami Beach",
    "state": "Florida",
    "country": "USA",
    "postal_code": "33139",
    "latitude": 25.7907,
    "longitude": -80.1300
  },
  "is_active": true,
  "is_featured": false,
  "verification_status": "pending",
  "average_rating": 0.0,
  "total_reviews": 0,
  "images": [...],
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "published_at": null
}
```

### Paginated List Response (200)

```json
{
  "items": [
    {
      "id": "property-uuid-1",
      "title": "Beach Villa",
      "slug": "beach-villa",
      "property_type": "entire_place",
      "price_per_night": 45000,
      "currency": "USD",
      "bedrooms": 4,
      "beds": 5,
      "bathrooms": 3.5,
      "max_guests": 8,
      "average_rating": 4.8,
      "total_reviews": 24,
      "is_featured": true,
      "location": {...},
      "cover_image": "https://example.com/image.jpg"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### Error Responses

#### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "price_per_night"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ],
  "message": "Validation error"
}
```

#### Unauthorized (401)

```json
{
  "detail": "Could not validate credentials"
}
```

#### Forbidden (403)

```json
{
  "detail": "You don't have permission to update this property"
}
```

#### Not Found (404)

```json
{
  "detail": "Property not found"
}
```

#### Bad Request (400)

```json
{
  "detail": "Property must have at least 3 images"
}
```

## Testing with Python requests

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create property
property_data = {
    "title": "Test Property",
    "description": "A test property description that is long enough for validation.",
    "property_type": "entire_place",
    "bedrooms": 2,
    "beds": 2,
    "bathrooms": 1.5,
    "max_guests": 4,
    "price_per_night": 15000,
    "location": {
        "address": "123 Test St",
        "city": "Test City",
        "country": "Test Country",
        "latitude": 0.0,
        "longitude": 0.0
    },
    "images": [
        {"image_url": "https://example.com/1.jpg", "display_order": 0, "is_cover": True},
        {"image_url": "https://example.com/2.jpg", "display_order": 1},
        {"image_url": "https://example.com/3.jpg", "display_order": 2}
    ]
}

response = requests.post(
    f"{BASE_URL}/properties/",
    json=property_data,
    headers=headers
)

if response.status_code == 201:
    property_id = response.json()["id"]
    print(f"Property created: {property_id}")
else:
    print(f"Error: {response.json()}")

# Search properties
params = {
    "city": "Miami",
    "min_price": 10000,
    "max_price": 50000,
    "bedrooms": 2,
    "page": 1,
    "page_size": 10
}

response = requests.get(f"{BASE_URL}/properties/", params=params)
properties = response.json()
print(f"Found {properties['total']} properties")
```

## Common Query Parameters

### Pagination
- `page`: Page number (default: 1, min: 1)
- `page_size`: Items per page (default: 20, min: 1, max: 100)

### Sorting
- `sort_by`: Sort order
  - `price_asc`: Price low to high
  - `price_desc`: Price high to low
  - `rating`: Highest rated first
  - `newest`: Most recently added first

### Property Filters
- `property_type`: `entire_place`, `private_room`, `shared_room`
- `city`: City name (case-insensitive partial match)
- `country`: Country name (case-insensitive partial match)
- `min_price`: Minimum price in cents
- `max_price`: Maximum price in cents
- `bedrooms`: Minimum number of bedrooms
- `beds`: Minimum number of beds
- `bathrooms`: Minimum number of bathrooms
- `max_guests`: Minimum guest capacity
- `instant_book`: `true` or `false`

### Search Specific
- `location`: City or country search term
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `adults`: Number of adults
- `children`: Number of children
- `infants`: Number of infants
- `pets`: Pet-friendly properties (`true`/`false`)
- `amenities`: Comma-separated amenity IDs

### Location Based
- `lat`: Latitude
- `lng`: Longitude
- `radius`: Search radius in kilometers

## Rate Limiting

Current rate limits (configurable):
- 60 requests per minute per IP
- Headers returned:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## WebSocket Support (Future)

Real-time updates for bookings and messages will be available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Best Practices

### 1. Always Use HTTPS in Production
```bash
curl https://api.example.com/api/v1/properties/
```

### 2. Handle Pagination
```python
def get_all_properties():
    all_properties = []
    page = 1
    
    while True:
        response = requests.get(
            f"{BASE_URL}/properties/",
            params={"page": page, "page_size": 100}
        )
        data = response.json()
        all_properties.extend(data["items"])
        
        if page >= data["total_pages"]:
            break
        page += 1
    
    return all_properties
```

### 3. Implement Retry Logic
```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### 4. Cache Responses
```python
import requests_cache

# Cache GET requests for 5 minutes
requests_cache.install_cache('property_cache', expire_after=300)
```

### 5. Validate Input Before Sending
```python
from pydantic import BaseModel, validator

class PropertyCreate(BaseModel):
    title: str
    description: str
    price_per_night: int
    
    @validator('title')
    def title_min_length(cls, v):
        if len(v) < 10:
            raise ValueError('Title must be at least 10 characters')
        return v
    
    @validator('price_per_night')
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

## Integration Examples

### Next.js Frontend Integration

```typescript
// lib/api/properties.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const propertyApi = {
  async getProperties(filters?: PropertyFilters) {
    const response = await axios.get(`${API_URL}/api/v1/properties/`, {
      params: filters
    });
    return response.data;
  },

  async getProperty(id: string) {
    const response = await axios.get(`${API_URL}/api/v1/properties/${id}`);
    return response.data;
  },

  async createProperty(data: PropertyCreate, token: string) {
    const response = await axios.post(
      `${API_URL}/api/v1/properties/`,
      data,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.data;
  }
};
```

### React Hook Example

```typescript
// hooks/useProperties.ts
import { useQuery } from '@tanstack/react-query';
import { propertyApi } from '@/lib/api/properties';

export function useProperties(filters?: PropertyFilters) {
  return useQuery({
    queryKey: ['properties', filters],
    queryFn: () => propertyApi.getProperties(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProperty(id: string) {
  return useQuery({
    queryKey: ['property', id],
    queryFn: () => propertyApi.getProperty(id),
    enabled: !!id,
  });
}
```

## Monitoring & Debugging

### Check Service Health

```bash
curl http://localhost:8001/health
```

### View API Documentation

```bash
# Open in browser
open http://localhost:8001/docs
```

### Monitor Logs

```bash
# Docker logs
docker-compose logs -f listing-service

# Application logs
tail -f logs/app.log
```

### Database Queries

```bash
# Check slow queries
docker-compose exec postgres psql -U listing_user -d listing_db -c \
  "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

## Troubleshooting

### 401 Unauthorized
- Check token expiration
- Verify token format: `Bearer <token>`
- Ensure auth service is running

### 422 Validation Error
- Check request payload against schema
- Ensure all required fields are provided
- Verify data types match

### 503 Service Unavailable
- Check database connection
- Verify PostgreSQL is running
- Check auth service availability

### Slow Response Times
- Add database indexes
- Enable caching
- Optimize queries
- Check database connection pool

## Additional Resources

- **OpenAPI Spec**: http://localhost:8001/openapi.json
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **GitHub**: [Repository URL]
- **Documentation**: [Docs URL]
