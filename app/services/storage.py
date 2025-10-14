import os
import uuid
from datetime import datetime
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

from app.config import settings


class StorageService:
    def __init__(self):
        self.environment = settings.ENVIRONMENT

        # Initialize S3 client for production
        if self.environment == "production":
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                raise Exception(f"Failed to initialize S3 client: {str(e)}")

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename with timestamp and UUID"""
        ext = original_filename.split('.')[-1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}.{ext}"

    def _validate_image(self, file: UploadFile) -> bool:
        """Validate image file"""
        # Check file extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '.{ext}' not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Check file size
        file.file.seek(0, 2)  # Move to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )

        # Validate it's actually an image
        try:
            image = Image.open(file.file)
            image.verify()
            file.file.seek(0)  # Reset file pointer after verification
            return True
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

    async def upload_to_s3(
        self,
        file: UploadFile,
        folder: Optional[str] = None
    ) -> str:
        """Upload file to S3 bucket"""
        try:
            # Generate unique filename
            filename = self._generate_unique_filename(file.filename)

            # Create S3 key (path)
            s3_folder = folder or settings.S3_FOLDER
            s3_key = f"{s3_folder}/{filename}"

            # Read file content
            file_content = await file.read()

            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
                ACL='public-read',  # Make file publicly accessible
                CacheControl='max-age=31536000',  # Cache for 1 year
            )

            # Generate URL
            if settings.CLOUDFRONT_DOMAIN:
                # Use CloudFront URL if available
                image_url = f"https://{settings.CLOUDFRONT_DOMAIN}/{s3_key}"
            else:
                # Use direct S3 URL
                image_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

            return image_url

        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to S3: {str(e)}"
            )
        except BotoCoreError as e:
            raise HTTPException(
                status_code=500,
                detail=f"AWS configuration error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during S3 upload: {str(e)}"
            )

    async def upload_to_local(
        self,
        file: UploadFile,
        subfolder: Optional[str] = None
    ) -> str:
        """Upload file to local media directory"""
        try:
            # Generate unique filename
            filename = self._generate_unique_filename(file.filename)

            # Create subdirectory if specified
            upload_dir = settings.MEDIA_DIR
            if subfolder:
                upload_dir = os.path.join(settings.MEDIA_DIR, subfolder)
                os.makedirs(upload_dir, exist_ok=True)

            # Full file path
            file_path = os.path.join(upload_dir, filename)

            # Write file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Generate URL
            relative_path = os.path.join(
                settings.MEDIA_DIR.replace('media/', ''),
                subfolder or '',
                filename
            ).replace('\\', '/')

            image_url = f"{settings.BASE_URL}/media/{relative_path}"

            return image_url

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file locally: {str(e)}"
            )

    async def upload_image(
        self,
        file: UploadFile,
        subfolder: Optional[str] = None
    ) -> str:
        """
        Upload image - automatically routes to S3 (production) or local (development)
        """
        # Validate image
        self._validate_image(file)

        # Upload based on environment
        if self.environment == "production":
            return await self.upload_to_s3(file, subfolder)
        else:
            return await self.upload_to_local(file, subfolder)

    def delete_from_s3(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key
            )
            return True
        except Exception as e:
            print(f"Failed to delete from S3: {str(e)}")
            return False

    def delete_from_local(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Failed to delete local file: {str(e)}")
            return False


# Create singleton instance
storage_service = StorageService()
