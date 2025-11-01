# app/models/vendor_service.py

import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base

class VendorService(Base):
    __tablename__ = "vendor_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendorId = Column(UUID(as_uuid=True), nullable=False, index=True)
    vendorName = Column(String, nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in hours or a relevant unit
    allowedGuests = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)

    # Storing structured data like service area is best done with JSONB in PostgreSQL
    serviceArea = Column(JSONB, nullable=False)

    # Rating and review info
    rating = Column(Float, default=0)
    reviewCount = Column(Integer, default=0)

    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Assuming a relationship to VendorService
    serviceId = Column(UUID(as_uuid=True), ForeignKey("vendor_services.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True, index=True)

    # 'percentage' or 'fixed'
    discountType = Column(String, nullable=False, default="percentage")
    discountValue = Column(Float, nullable=False)

    validFrom = Column(DateTime(timezone=True), nullable=False)
    validTo = Column(DateTime(timezone=True), nullable=False)

    usageLimit = Column(Integer, nullable=False)
    usedCount = Column(Integer, default=0)

    eligibility = Column(String, nullable=True)
    terms = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)

    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
