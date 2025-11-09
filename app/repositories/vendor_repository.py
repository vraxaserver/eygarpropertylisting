# app/repositories/vendor_service.py

from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.vendor import VendorService, Coupon
from app.schemas.vendor import VendorServiceUpdate, CouponCreate, CouponUpdate
from sqlalchemy.orm import joinedload

class VendorServiceRepository:
    async def get_by_id(self, db: AsyncSession, service_id: UUID) -> Optional[VendorService]:
        return await db.get(VendorService, service_id)

    async def get_all(self, db: AsyncSession, skip: int, limit: int) -> List[VendorService]:
        result = await db.execute(select(VendorService).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_vendor_id(self, db: AsyncSession, vendor_id: UUID) -> List[VendorService]:
        result = await db.execute(select(VendorService).where(VendorService.vendorId == vendor_id))
        return result.scalars().all()

    async def create(self, db: AsyncSession, db_obj: VendorService) -> VendorService:
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: VendorService, obj_in: VendorServiceUpdate
    ) -> VendorService:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: VendorService) -> None:
        await db.delete(db_obj)
        await db.flush()


class CouponRepository:

    async def get_by_id(self, db: AsyncSession, coupon_id: str) -> Optional[Coupon]:
        result = await db.execute(select(Coupon).filter(Coupon.id == coupon_id))
        return result.scalars().first()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Coupon]:
        result = await db.execute(select(Coupon).filter(Coupon.code == code))
        return result.scalars().first()

    async def list_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Coupon]:
        query = (
            select(Coupon)
            .options(
                joinedload(Coupon.service)  # <-- This tells SQLAlchemy to JOIN the service table
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        # result = await db.execute(select(Coupon).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, coupon_data: CouponCreate) -> Coupon:
        db_coupon = Coupon(**coupon_data.dict())
        db.add(db_coupon)
        await db.commit()
        await db.refresh(db_coupon)
        return db_coupon

    async def update(self, db: AsyncSession, coupon: Coupon, coupon_data: CouponUpdate) -> Coupon:
        update_data = coupon_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(coupon, key, value)

        await db.commit()
        await db.refresh(coupon)
        return coupon

    async def delete(self, db: AsyncSession, coupon: Coupon) -> None:
        await db.delete(coupon)
        await db.commit()
