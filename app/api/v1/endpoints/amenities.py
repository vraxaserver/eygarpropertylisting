from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.amenity import AmenityResponse, SafetyFeatureResponse, AmenityCreate, SafetyFeatureCreate
from app.models.amenity import Amenity, SafetyFeature
from app.dependencies import get_current_active_user
from app.schemas.common import UserInfo


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


@router.post("/amenities", response_model=AmenityResponse, status_code=status.HTTP_201_CREATED)
async def create_amenity(
    amenity_in: AmenityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """
    Create a new amenity.
    Requires authentication.
    """
    # Check if amenity name already exists
    existing = await db.execute(select(Amenity).where(Amenity.name == amenity_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amenity with this name already exists"
        )
    
    amenity = Amenity(**amenity_in.model_dump())
    db.add(amenity)
    await db.flush()
    await db.refresh(amenity)
    return amenity


@router.get("/safety-features", response_model=List[SafetyFeatureResponse])
async def list_safety_features(db: AsyncSession = Depends(get_db)):
    """
    Get all available safety features.
    Public endpoint - no authentication required.
    """
    result = await db.execute(select(SafetyFeature).order_by(SafetyFeature.name))
    safety_features = result.scalars().all()
    return list(safety_features)


@router.post("/safety-features", response_model=SafetyFeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_feature(
    feature_in: SafetyFeatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """
    Create a new safety feature.
    Requires authentication.
    """
    # Check if safety feature name already exists
    existing = await db.execute(select(SafetyFeature).where(SafetyFeature.name == feature_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Safety feature with this name already exists"
        )
    
    feature = SafetyFeature(**feature_in.model_dump())
    db.add(feature)
    await db.flush()
    await db.refresh(feature)
    return feature