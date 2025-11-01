# app/api/vendor_service.py

from fastapi import APIRouter, Depends, status, Response
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.common import UserInfo
from app.services.vendor_service import VendorServiceService
from app.schemas.vendor import VendorServiceCreate, VendorServiceUpdate, VendorServiceResponse

router = APIRouter()

# Dependency to get the service layer instance
def get_vendor_service() -> VendorServiceService:
    return VendorServiceService()

@router.get("/services", response_model=List[VendorServiceResponse])
async def list_services(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """List all available services with pagination."""
    return await service.get_all_services(db, skip=pagination.skip, limit=pagination.limit)

@router.get("/services/my", response_model=List[VendorServiceResponse])
async def list_my_services(
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """List all services for the currently logged-in user."""
    return await service.get_services_by_vendor_id(db, vendor_id=current_user.id)

@router.get("/{vendor_id}/services", response_model=List[VendorServiceResponse])
async def list_services_by_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """List all services for a specific vendor by their ID."""
    return await service.get_services_by_vendor_id(db, vendor_id=vendor_id)

@router.get("/services/{service_id}", response_model=VendorServiceResponse)
async def get_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """Get a single service by its ID."""
    return await service.get_service_by_id(db, service_id=service_id)

@router.post("/services", response_model=VendorServiceResponse, status_code=status.HTTP_201_CREATED)
async def add_service(
    service_create: VendorServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """Add a new service. User must be authenticated."""
    return await service.create_service(db, service_create=service_create, current_user=current_user)

@router.put("/services/{service_id}", response_model=VendorServiceResponse)
async def edit_service(
    service_id: UUID,
    service_update: VendorServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """Edit an existing service. User must be the owner of the service."""
    return await service.update_service(db, service_id=service_id, service_update=service_update, current_user=current_user)

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user),
    service: VendorServiceService = Depends(get_vendor_service)
):
    """Delete a service. User must be the owner of the service."""
    await service.delete_service(db, service_id=service_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
