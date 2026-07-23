import os
import aiofiles
import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
from app.config import settings  # Assuming you have a settings module
from pathlib import Path

# Initialize S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

async def save_image_file(file: UploadFile, property_id: str, file_name: str) -> str:
    """
    Saves a file based on the current environment and returns the accessible URL/Path.
    """
    env = settings.ENVIRONMENT.lower()

    # 1. LOCAL ENVIRONMENT
    if env == "local":
        # logic: media/properties/[property_id]/[filename]
        base_path = f"media/properties/{property_id}"
        os.makedirs(base_path, exist_ok=True)

        file_path = os.path.join(base_path, file_name)

        # Async write to disk
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Return absolute URL using BASE_URL
        base_url = settings.BASE_URL if settings.BASE_URL.endswith("/") else f"{settings.BASE_URL}/"
        clean_path = file_path.replace("\\", "/")
        return f"{base_url}{clean_path}"

    # 2. CLOUD ENVIRONMENT (DEV / PROD)
    else:
        bucket_name = settings.S3_BUCKET_NAME or ("eygar-dev" if env == "dev" else "eygar-prod")
        s3_key = f"properties/{property_id}/images/{file_name}"

        try:
            # Reset file cursor before upload
            await file.seek(0)
            file_obj = file.file

            # Upload to S3
            s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': file.content_type}
            )

            # Return the S3 URL
            # Format: https://[bucket].s3.[region].amazonaws.com/[key]
            return f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

        except NoCredentialsError:
            print("AWS Credentials not available")
            raise
        except Exception as e:
            print(f"Failed to upload to S3: {str(e)}")
            raise
