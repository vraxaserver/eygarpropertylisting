from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.common import UserInfo, PaginatedResponse
from app.schemas.property import PropertyListResponse
from app.services.property_service import PropertyService


router = APIRouter()


@router.get("/my-properties", response_model=PaginatedResponse[PropertyListResponse])
async def get_my_properties(
    pagination: PaginationParams = Depends(),
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all properties owned by the authenticated user.
    Requires authentication.
    """
    service = PropertyService(db)
    properties, total = await service.get_user_properties(
        current_user.id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
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