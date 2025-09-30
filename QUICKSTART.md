# 🚀 Quick Start Guide

Get the Property Listing Microservice up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11 or higher installed
- [ ] Docker and Docker Compose installed
- [ ] Auth service running on `localhost:8000`
- [ ] Git installed

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd listing-service
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update these critical values:
- `DATABASE_URL` - Your PostgreSQL connection string
- `JWT_SECRET_KEY` - Must match your auth service secret
- `AUTH_SERVICE_URL` - URL of your auth service (default: http://127.0.0.1:8000)

### 5. Start Database

```bash
docker-compose up -d postgres
```

Wait for database to be healthy (about 10 seconds):
```bash
docker-compose ps
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Seed Sample Data (Optional)

```bash
python scripts/seed_data.py
```

This creates:
- 20+ amenities
- 6 safety features  
- 3 sample properties

### 8. Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 9. Verify Installation

Open your browser and visit:
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "service": "Property Listing Service",
  "version": "1.0.0"
}
```

## 🎉 Success! Your service is running!

## Quick Test

### Test 1: List Properties

```bash
curl http://localhost:8001/api/v1/properties/
```

### Test 2: Get Amenities

```bash
curl http://localhost:8001/api/v1/amenities
```

### Test 3: Create Property (Requires Auth)

First, get a token from your auth service, then:

```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8001/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "title": "My First Property",
  "description": "A beautiful property in a great location with all the amenities you need.",
  "property_type": "entire_place",
  "bedrooms": 2,
  "beds": 2,
  "bathrooms": 1.5,
  "max_guests": 4,
  "max_adults": 4,
  "max_children": 2,
  "max_infants": 1,
  "price_per_night": 15000,
  "currency": "USD",
  "location": {
    "address": "123 Main St",
    "city": "Miami",
    "state": "Florida",
    "country": "USA",
    "postal_code": "33101",
    "latitude": 25.7617,
    "longitude": -80.1918
  },
  "images": [
    {"image_url": "https://picsum.photos/800/600?random=1", "display_order": 0, "is_cover": true},
    {"image_url": "https://picsum.photos/800/600?random=2", "display_order": 1},
    {"image_url": "https://picsum.photos/800/600?random=3", "display_order": 2}
  ],
  "house_rules": ["No smoking", "No parties"]
}
EOF
```

## Using Make Commands (Easier!)

If you have `make` installed:

```bash
# Complete setup with one command
make dev-setup

# Start server
make run

# Run tests
make test

# View all available commands
make help
```

## Next Steps

1. **Explore API Documentation**: Visit http://localhost:8001/docs
2. **Read API Examples**: Check `API_EXAMPLES.md` for detailed usage
3. **Run Tests**: Execute `pytest` to run the test suite
4. **Integrate with Frontend**: Connect your Next.js app
5. **Customize**: Modify models and endpoints for your needs

## Common Issues & Solutions

### Issue: Database Connection Error

**Error**: `could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Issue: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process (replace PID)
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8002
```

### Issue: Auth Service Not Found

**Error**: `Auth service unavailable`

**Solution**:
1. Ensure auth service is running on `localhost:8000`
2. Check `AUTH_SERVICE_URL` in `.env`
3. Verify network connectivity:
```bash
curl http://localhost:8000/api/auth/me/
```

### Issue: Migration Errors

**Error**: `Target database is not up to date`

**Solution**:
```bash
# Check current migration
alembic current

# Upgrade to latest
alembic upgrade head

# If issues persist, reset (DEV ONLY!)
alembic downgrade base
alembic upgrade head
```

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Run from project root
cd listing-service
python -m uvicorn app.main:app
```

## Development Workflow

### Making Changes

1. **Add a new endpoint**:
   - Create endpoint in `app/api/v1/endpoints/`
   - Add to router in `app/api/v1/router.py`
   - Write tests in `tests/`

2. **Modify database**:
   - Update models in `app/models/`
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Review migration in `alembic/versions/`
   - Apply: `alembic upgrade head`

3. **Add business logic**:
   - Create service in `app/services/`
   - Add repository methods in `app/repositories/`
   - Update schemas in `app/schemas/`

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_properties.py

# With coverage
pytest --cov=app --cov-report=html

# Watch mode (requires pytest-watch)
ptw
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking (if using mypy)
mypy app/
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t listing-service:latest .
```

### Run Container

```bash
docker run -d \
  --name listing-service \
  -p 8001:8001 \
  --env-file .env \
  listing-service:latest
```

### With Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Production Deployment

For production, consider:

1. **Use production-grade server**:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Set environment to production**:
```bash
DEBUG=False
LOG_LEVEL=WARNING
```

3. **Use proper secrets management** (AWS Secrets Manager, Vault, etc.)

4. **Enable HTTPS** with proper certificates

5. **Setup monitoring** (Prometheus, Grafana, Sentry)

6. **Configure backup** for PostgreSQL

7. **Implement rate limiting** (Redis + FastAPI middleware)

## Useful Commands Reference

```bash
# Database
make db-shell                    # Open PostgreSQL shell
alembic current                  # Show current migration
alembic history                  # Show migration history

# Development
make dev-setup                   # Complete dev setup
make run                         # Start dev server
make test                        # Run tests
make clean                       # Clean cache files

# Docker
docker-compose up -d             # Start services
docker-compose down              # Stop services
docker-compose logs -f           # Follow logs
docker-compose restart           # Restart services

# Python
pip list                         # List installed packages
pip freeze > requirements.txt    # Update requirements
python -m pytest -v              # Verbose test output
```

## Support & Resources

- **Documentation**: http://localhost:8001/docs
- **GitHub Issues**: [Create an issue]
- **API Examples**: See `API_EXAMPLES.md`
- **Full README**: See `README.md`

## What's Next?

Now that your service is running:

✅ Test all endpoints with the interactive docs  
✅ Integrate with your Next.js frontend  
✅ Connect to your Django auth service  
✅ Add custom business logic  
✅ Deploy to production  

Happy coding! 🎉