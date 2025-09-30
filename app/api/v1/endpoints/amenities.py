from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.amenity import AmenityResponse, SafetyFeatureResponse
from app.models.amenity import Amenity, SafetyFeature


router = APIRouter()


@router.get("/amenities", response_model=List[AmenityResponse])
async def list_amenities(db: AsyncSession = Depends(get_db)):
    """
    Get all available amenities.
    Public endpoint - no authentication required.
    """
    result = await db.execute(select(Amenity).order_by(Amenity.category, Amenity.name))
    amenities = result.scalars().all()
    return list(amenities)


@router.get("/safety-features", response_model=List[SafetyFeatureResponse])
async def list_safety_features(db: AsyncSession = Depends(get_db)):
    """
    Get all available safety features.
    Public endpoint - no authentication required.
    """
    result = await db.execute(select(SafetyFeature).order_by(SafetyFeature.name))
    safety_features = result.scalars().all()
    return list(safety_features)