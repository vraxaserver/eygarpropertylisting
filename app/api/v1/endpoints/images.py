from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from app.services.storage import storage_service
from app.config import settings


router = APIRouter()


class ImageUploadResponse(BaseModel):
    image_url: str
    filename: str
    display_order: int
    is_cover: bool
    alt_text: str
    message: str = "Image uploaded successfully"


class ImageDeleteRequest(BaseModel):
    image_url: str


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    image: UploadFile = File(..., description="Image file to upload"),
    display_order: int = Form(0, description="Display order of the image"),
    is_cover: bool = Form(False, description="Whether this is the cover image"),
    alt_text: str = Form("", description="Alternative text for the image"),
):
    """
    Upload an image file

    - **image**: Image file (jpg, jpeg, png, gif, webp)
    - **display_order**: Order in which image should be displayed
    - **is_cover**: Boolean indicating if this is the cover image
    - **alt_text**: Alternative text description for the image

    Returns the uploaded image URL
    """
    try:
        # Upload image
        image_url = await storage_service.upload_image(
            file=image,
            subfolder="properties"  # You can make this dynamic
        )

        return ImageUploadResponse(
            image_url=image_url,
            filename=image.filename,
            display_order=display_order,
            is_cover=is_cover,
            alt_text=alt_text or image.filename,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/upload-multiple")
async def upload_multiple_images(
    images: list[UploadFile] = File(..., description="Multiple image files"),
):
    """
    Upload multiple images at once

    Returns list of uploaded image URLs
    """
    try:
        uploaded_images = []

        for index, image in enumerate(images):
            image_url = await storage_service.upload_image(
                file=image,
                subfolder="properties"
            )

            uploaded_images.append({
                "image_url": image_url,
                "filename": image.filename,
                "display_order": index,
                "is_cover": index == 0,
                "alt_text": image.filename,
            })

        return {
            "message": f"Successfully uploaded {len(uploaded_images)} images",
            "images": uploaded_images
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload images: {str(e)}"
        )


@router.delete("/delete")
async def delete_image(request: ImageDeleteRequest):
    """
    Delete an image from storage
    """
    try:
        if settings.ENVIRONMENT == "production":
            # Extract S3 key from URL
            s3_key = request.image_url.split('.com/')[-1]
            success = storage_service.delete_from_s3(s3_key)
        else:
            # Extract local file path from URL
            file_path = request.image_url.replace(settings.BASE_URL, '').lstrip('/')
            success = storage_service.delete_from_local(file_path)

        if success:
            return {"message": "Image deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check if image upload service is working"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "storage": "s3" if settings.ENVIRONMENT == "production" else "local"
    }
