import asyncio
import sys
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile

# Add current dir to python path
sys.path.append(str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.services.property_service import PropertyService

async def main():
    payload = {
        "title": "Objects are the fundamental entities stored in Amazon S3.",
        "description": "Objects are the fundamental entities stored in Amazon S3. Objects are the fundamental entities stored in Amazon S3.",
        "property_type": "house",
        "place_type": "entire_place",
        "is_owner": True,
        "is_agent": False,
        "revenue_share_type": "percentage",
        "revenue_share": 0,
        "bedrooms": 1,
        "beds": 1,
        "bathrooms": 1,
        "max_guests": 2,
        "max_adults": 2,
        "max_children": 0,
        "max_infants": 0,
        "pets_allowed": False,
        "price_per_night": 12300,
        "currency": "USD",
        "cleaning_fee": 0,
        "service_fee": 0,
        "weekly_discount": 0,
        "monthly_discount": 0,
        "instant_book": False,
        "location": {
            "address": "Al Jadeed",
            "city": "Doha",
            "state": "",
            "country": "Qatar",
            "postal_code": "",
            "latitude": 0.0,
            "longitude": 0.0
        },
        "images": [
            {
                "display_order": 0,
                "is_cover": True,
                "alt_text": "639bc635-1e17-4733-a1c2-097283d44f38.avif",
                "image_url": ""
            },
            {
                "display_order": 1,
                "is_cover": False,
                "alt_text": "1111.png",
                "image_url": ""
            },
            {
                "display_order": 2,
                "is_cover": False,
                "alt_text": "354690571.jpg",
                "image_url": ""
            },
            {
                "display_order": 3,
                "is_cover": False,
                "alt_text": "414226708.jpg",
                "image_url": ""
            },
            {
                "display_order": 4,
                "is_cover": False,
                "alt_text": "415912723.jpg",
                "image_url": ""
            }
        ],
        "amenity_ids": [],
        "house_rules": ["Rule one"],
        "cancellation_policy": "Objects are the fundamental entities stored in Amazon S3.",
        "check_in_policy": "Objects are the fundamental entities stored in Amazon S3."
    }
    
    # Create mock UploadFile objects
    mock_files = [
        UploadFile(filename="file1.png", file=BytesIO(b"fake image data 1")),
        UploadFile(filename="file2.png", file=BytesIO(b"fake image data 2")),
        UploadFile(filename="file3.png", file=BytesIO(b"fake image data 3")),
        UploadFile(filename="file4.png", file=BytesIO(b"fake image data 4")),
        UploadFile(filename="file5.png", file=BytesIO(b"fake image data 5")),
    ]
    
    from uuid import uuid4
    host_id = uuid4()
    async with AsyncSessionLocal() as db:
        service = PropertyService(db)
        try:
            res = await service.create_property(
                property_data=payload,
                host_id=host_id,
                host_name="Test Host",
                host_email="test@example.com",
                host_avatar=None,
                image_files=mock_files
            )
            print("Success:", res)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
