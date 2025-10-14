from fastapi import APIRouter
from app.api.v1.endpoints import properties, reviews, amenities, my_properties, experiences, images


api_router = APIRouter()

# Property endpoints
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])

# Review endpoints
api_router.include_router(reviews.router, tags=["reviews"])

# Amenities and safety features
api_router.include_router(amenities.router, tags=["amenities"])

# My properties
api_router.include_router(my_properties.router, tags=["my-properties"])

# Experiences
api_router.include_router(experiences.router, prefix="/experiences", tags=["experiences"])

api_router.include_router(images.router, prefix="/images", tags=["images"])
