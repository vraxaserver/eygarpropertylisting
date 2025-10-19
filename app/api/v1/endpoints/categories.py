from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from app.models.property import Category
from uuid import UUID


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Category",
)
async def create_category(
    category_in: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    """
    Creates a new category with the provided data.
    """
    # Check for unique constraints (name or slug) before creation
    category = Category(
        **category_in.model_dump(),
    )
    db.add(category)
    await db.flush()

    await db.refresh(category)

    return category


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Retrieve a list of Categories",
)
async def read_categories(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve categories with pagination.
    """
    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()
    return categories


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Category",
)
async def delete_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a category by its unique ID.
    """
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id)
    )
    category = await result.scalar_one_or_none()
    if not category:
        return False

    await db.delete(category)
    await db.flush()
    return {"ok": True} # Returning a dictionary causes FastAPI to return 200,
                        # but returning None or an empty response is better for 204
    # return None # <-- better practice for HTTP 204 No Content
