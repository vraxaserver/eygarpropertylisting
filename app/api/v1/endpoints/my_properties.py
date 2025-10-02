from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.common import UserInfo, PaginatedResponse
from app.schemas.property import PropertyListResponse
from app.services.property_service import PropertyService
from app.api.v1.endpoints.properties import property_to_list_response

router = APIRouter()


@router.get("/my-properties", response_model=PaginatedResponse[PropertyListResponse])
async def get_my_properties(
    pagination: PaginationParams = Depends(),
    current_user: UserInfo = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all properties owned by the authenticated host."""
    if not current_user.host_info or not current_user.host_info.id:
        return PaginatedResponse.create(
            items=[],
            total=0,
            page=pagination.page,
            page_size=pagination.page_size
        )
    
    service = PropertyService(db)
    properties, total = await service.get_host_properties(
        current_user.host_info.id,
        skip=pagination.skip,
        limit=pagination.limit
    )
    
    property_list = [property_to_list_response(prop) for prop in properties]
    
    return PaginatedResponse.create(
        items=property_list,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )