# app/api/v1/endpoints/coupon.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.common import UserInfo
from app.dependencies import get_current_active_user, PaginationParams
from app.schemas.vendor import Coupon, CouponCreate, CouponUpdate, CouponResponse
from app.services.vendor_service import CouponService

router = APIRouter()

# Dependency to get the service layer instance
def get_coupon_service() -> CouponService:
    return CouponService()

@router.post("/coupons", response_model=Coupon, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user),
    service: CouponService = Depends(get_coupon_service)
):
    """
    Create a new coupon.
    A unique code will be generated if not provided.
    """
    return await service.create_coupon(db, coupon_data)

@router.get("/coupons", response_model=List[CouponResponse])
async def list_coupons(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    service: CouponService = Depends(get_coupon_service)
):
    """
    Retrieve a list of all coupons with pagination.
    """
    return await service.list_coupons(db, skip, limit)

@router.get("/coupons/{coupon_id}", response_model=Coupon)
async def get_coupon(
    coupon_id: str,
    service: CouponService = Depends(get_db)
):
    """
    Retrieve details of a specific coupon by its ID.
    """
    return await service.get_coupon(coupon_id)

@router.put("/coupons/{coupon_id}", response_model=Coupon)
async def update_coupon(
    coupon_id: str,
    coupon_data: CouponUpdate,
    service: CouponService = Depends(get_db)
):
    """
    Update the details of an existing coupon.
    """
    return await service.update_coupon(coupon_id, coupon_data)

@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: str,
    service: CouponService = Depends(get_db)
):
    """
    Delete a coupon by its ID.
    """
    await service.delete_coupon(coupon_id)
    # A 204 response should not have a body
    return None
