# app/services/vendor_service.py

from uuid import UUID
from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.vendor_repository import VendorServiceRepository, CouponRepository
from app.schemas.vendor import VendorServiceCreate, VendorServiceUpdate, CouponCreate, CouponUpdate
from app.schemas.common import UserInfo
from app.models.vendor import VendorService


class VendorServiceService:
    def __init__(self):
        self.repository = VendorServiceRepository()

    async def get_all_services(self, db: AsyncSession, skip: int, limit: int) -> List[VendorService]:
        return await self.repository.get_all(db, skip=skip, limit=limit)

    async def get_service_by_id(self, db: AsyncSession, service_id: UUID) -> VendorService:
        db_service = await self.repository.get_by_id(db, service_id=service_id)
        if not db_service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        return db_service

    async def get_services_by_vendor_id(self, db: AsyncSession, vendor_id: UUID) -> List[VendorService]:
        return await self.repository.get_by_vendor_id(db, vendor_id=vendor_id)

    async def create_service(
        self, db: AsyncSession, service_create: VendorServiceCreate, current_user: UserInfo
    ) -> VendorService:
        service_data = service_create.model_dump()
        db_service = VendorService(
            **service_data,
            vendorId=current_user.id,
            vendorName=f"{current_user.first_name} {current_user.last_name}".strip()
        )
        return await self.repository.create(db, db_obj=db_service)

    async def update_service(
        self, db: AsyncSession, service_id: UUID, service_update: VendorServiceUpdate, current_user: UserInfo
    ) -> VendorService:
        db_service = await self.get_service_by_id(db, service_id)

        # Authorization check
        if db_service.vendorId != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this service")

        return await self.repository.update(db, db_obj=db_service, obj_in=service_update)

    async def delete_service(self, db: AsyncSession, service_id: UUID, current_user: UserInfo) -> None:
        db_service = await self.get_service_by_id(db, service_id)

        # Authorization check
        if db_service.vendorId != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this service")

        await self.repository.delete(db, db_obj=db_service)


class CouponService:
    def __init__(self):
        self.repo = CouponRepository()

    async def create_coupon(self, db: AsyncSession, coupon_data: CouponCreate):
        # Check if coupon code already exists
        existing_coupon = await self.repo.get_by_code(db, coupon_data.code)
        if existing_coupon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Coupon with code '{coupon_data.code}' already exists.",
            )

        # Ensure 'validTo' is after 'validFrom'
        if coupon_data.validTo <= coupon_data.validFrom:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="'validTo' date must be after 'validFrom' date."
            )

        return await self.repo.create(db, coupon_data)

    async def get_coupon(self, coupon_id: str):
        coupon = await self.repo.get_by_id(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coupon with id '{coupon_id}' not found.",
            )
        return coupon

    async def list_coupons(self, db: AsyncSession, skip: int, limit: int):
        return await self.repo.list_all(db, skip, limit)

    async def update_coupon(self, coupon_id: str, coupon_data: CouponUpdate):
        coupon_to_update = await self.get_coupon(coupon_id) # Reuse getter to handle not found case
        return await self.repo.update(coupon_to_update, coupon_data)

    async def delete_coupon(self, coupon_id: str):
        coupon_to_delete = await self.get_coupon(coupon_id) # Reuse getter to handle not found case
        await self.repo.delete(coupon_to_delete)
        return coupon_to_delete # Or return None as per preference
