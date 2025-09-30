from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams, get_optional_user
from app.schemas.common import UserInfo, PaginatedResponse, MessageResponse
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListResponse
)
from app.services.property_service import PropertyService
from app.models.property import PropertyType


router = APIRouter()


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new property listing.
    Requires authentication. Minimum 3 images required.
    """
    service = PropertyService(db)
    property_obj = await service.create_property(property_data, current_user.id)
    return property_obj


@router.get("/", response_model=PaginatedResponse[PropertyListResponse])
async def list_properties(
    pagination: PaginationParams = Depends(),
    property_type: Optional[PropertyType] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    min_price: Optional[int] = Query(None, description="Minimum price in cents"),
    max_price: Optional[int] = Query(None, description="Maximum price in cents"),
    bedrooms: Optional[int] = Query(None, ge=0),
    beds: Optional[int] = Query(None, ge=0),
    bathrooms: Optional[float] = Query(None, ge=0),
    max_guests: Optional[int] = Query(None, gt=0),
    instant_book: Optional[bool] = None,
    sort_by: Optional[str] = Query("newest", regex="^(price_asc|price_desc|rating|newest)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all properties with filtering and pagination.
    Public endpoint - no authentication required.
    """
    filters = {
        'is_active': True,
        'property_type': property_type,
        'city': city,
        'country': country,
        'min_price': min_price,
        'max_price': max_price,
        'bedrooms': bedrooms,
        'beds': beds,
        'bathrooms': bathrooms,
        'max_guests': max_guests,
        'instant_book': instant_book,
        'sort_by': sort_by
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    service = PropertyService(db)
    properties, total = await service.list_properties(
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Convert to list response format with cover image
    property_list = []
    for prop in properties:
        cover_image = next((img.image_url for img in prop.images if img.is_cover), None)
        if not cover_image and prop.images:
            cover_image = prop.images[0].image_url
        
        property_list.append(PropertyListResponse(
            id=prop.id,
            title=prop.title,
            slug=prop.slug,
            property_type=prop.property_type,
            price_per_night=prop.price_per_night,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            beds=prop.beds,
            bathrooms=prop.bathrooms,
            max_guests=prop.max_guests,
            average_rating=prop.average_rating,
            total_reviews=prop.total_reviews,
            is_featured=prop.is_featured,
            location=prop.location,
            cover_image=cover_image
        ))
    
    return PaginatedResponse.create(
        items=property_list,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/search", response_model=PaginatedResponse[PropertyListResponse])
async def search_properties(
    pagination: PaginationParams = Depends(),
    location: Optional[str] = Query(None, description="City or country name"),
    check_in: Optional[str] = Query(None, description="Check-in date (YYYY-MM-DD)"),
    check_out: Optional[str] = Query(None, description="Check-out date (YYYY-MM-DD)"),
    adults: Optional[int] = Query(None, ge=1),
    children: Optional[int] = Query(None, ge=0),
    infants: Optional[int] = Query(None, ge=0),
    pets: Optional[bool] = None,
    property_type: Optional[PropertyType] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bedrooms: Optional[int] = None,
    beds: Optional[int] = None,
    bathrooms: Optional[float] = None,
    amenities: Optional[str] = Query(None, description="Comma-separated amenity IDs"),
    instant_book: Optional[bool] = None,
    sort_by: Optional[str] = Query("newest", regex="^(price_asc|price_desc|rating|newest)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced search for properties with multiple filters.
    """
    filters = {
        'is_active': True,
        'property_type': property_type,
        'min_price': min_price,
        'max_price': max_price,
        'bedrooms': bedrooms,
        'beds': beds,
        'bathrooms': bathrooms,
        'instant_book': instant_book,
        'sort_by': sort_by
    }
    
    # Handle location search
    if location:
        # Simple implementation - search in city or country
        filters['city'] = location
    
    # Handle guest capacity
    if adults:
        total_guests = adults + (children or 0)
        filters['max_guests'] = total_guests
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    service = PropertyService(db)
    properties, total = await service.list_properties(
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Convert to list response
    property_list = []
    for prop in properties:
        cover_image = next((img.image_url for img in prop.images if img.is_cover), None)
        if not cover_image and prop.images:
            cover_image = prop.images[0].image_url
        
        property_list.append(PropertyListResponse(
            id=prop.id,
            title=prop.title,
            slug=prop.slug,
            property_type=prop.property_type,
            price_per_night=prop.price_per_night,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            beds=prop.beds,
            bathrooms=prop.bathrooms,
            max_guests=prop.max_guests,
            average_rating=prop.average_rating,
            total_reviews=prop.total_reviews,
            is_featured=prop.is_featured,
            location=prop.location,
            cover_image=cover_image
        ))
    
    return PaginatedResponse.create(
        items=property_list,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router.get("/featured", response_model=List[PropertyListResponse])
async def get_featured_properties(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get featured properties."""
    service = PropertyService(db)
    properties = await service.get_featured_properties(limit)
    
    property_list = []
    for prop in properties:
        cover_image = next((img.image_url for img in prop.images if img.is_cover), None)
        if not cover_image and prop.images:
            cover_image = prop.images[0].image_url
        
        property_list.append(PropertyListResponse(
            id=prop.id,
            title=prop.title,
            slug=prop.slug,
            property_type=prop.property_type,
            price_per_night=prop.price_per_night,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            beds=prop.beds,
            bathrooms=prop.bathrooms,
            max_guests=prop.max_guests,
            average_rating=prop.average_rating,
            total_reviews=prop.total_reviews,
            is_featured=prop.is_featured,
            location=prop.location,
            cover_image=cover_image
        ))
    
    return property_list


@router.get("/nearby", response_model=List[PropertyListResponse])
async def get_nearby_properties(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(10, ge=1, le=100, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search properties near coordinates."""
    service = PropertyService(db)
    properties = await service.search_nearby(lat, lng, radius, limit)
    
    property_list = []
    for prop in properties:
        cover_image = next((img.image_url for img in prop.images if img.is_cover), None)
        if not cover_image and prop.images:
            cover_image = prop.images[0].image_url
        
        property_list.append(PropertyListResponse(
            id=prop.id,
            title=prop.title,
            slug=prop.slug,
            property_type=prop.property_type,
            price_per_night=prop.price_per_night,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            beds=prop.beds,
            bathrooms=prop.bathrooms,
            max_guests=prop.max_guests,
            average_rating=prop.average_rating,
            total_reviews=prop.total_reviews,
            is_featured=prop.is_featured,
            location=prop.location,
            cover_image=cover_image
        ))
    
    return property_list


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    current_user: Optional[UserInfo] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get property details by ID.
    Public endpoint with optional authentication.
    """
    service = PropertyService(db)
    property_obj = await service.get_property(property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Only show inactive properties to owner
    if not property_obj.is_active:
        if not current_user or property_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
    
    return property_obj


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    update_data: PropertyUpdate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update property (owner only).
    Requires authentication.
    """
    service = PropertyService(db)
    
    try:
        property_obj = await service.update_property(property_id, update_data, current_user.id)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property_obj


@router.patch("/{property_id}", response_model=PropertyResponse)
async def partial_update_property(
    property_id: UUID,
    update_data: PropertyUpdate,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update property (owner only).
    Requires authentication.
    """
    return await update_property(property_id, update_data, current_user, db)


@router.delete("/{property_id}", response_model=MessageResponse)
async def delete_property(
    property_id: UUID,
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete property (owner only).
    Requires authentication.
    """
    service = PropertyService(db)
    
    try:
        deleted = await service.delete_property(property_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return MessageResponse(message="Property deleted successfully")


@router.get("/host/{user_id}", response_model=PaginatedResponse[PropertyListResponse])
async def get_host_properties(
    user_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get all properties listed by a specific host."""
    service = PropertyService(db)
    properties, total = await service.get_user_properties(
        user_id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    property_list = []
    for prop in properties:
        if not prop.is_active:
            continue
        
        cover_image = next((img.image_url for img in prop.images if img.is_cover), None)
        if not cover_image and prop.images:
            cover_image = prop.images[0].image_url
        
        property_list.append(PropertyListResponse(
            id=prop.id,
            title=prop.title,
            slug=prop.slug,
            property_type=prop.property_type,
            price_per_night=prop.price_per_night,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            beds=prop.beds,
            bathrooms=prop.bathrooms,
            max_guests=prop.max_guests,
            average_rating=prop.average_rating,
            total_reviews=prop.total_reviews,
            is_featured=prop.is_featured,
            location=prop.location,
            cover_image=cover_image
        ))
    
    return PaginatedResponse.create(
        items=property_list,
        total=len(property_list),
        page=pagination.page,
        page_size=pagination.page_size
    )