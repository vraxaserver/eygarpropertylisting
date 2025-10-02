"""
Script to populate host data for existing properties from auth service.
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.property import Property
import httpx
from app.config import settings


async def populate_host_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Property))
        properties = result.scalars().all()
        
        print(f"Found {len(properties)} properties to update")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for prop in properties:
                try:
                    response = await client.get(
                        f"{settings.AUTH_SERVICE_URL}/api/profiles/hosts/a7873814-e74b-499d-b297-c1f69947ace1/",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        host_data = response.json()
                        user_info = host_data.get("user_info")
                        print("user_info: ", user_info)
                        prop.host_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or "Host"
                        prop.host_email = user_info.get('email', '')
                        prop.host_avatar = user_info.get('avatar')
                        print(f"✓ Updated property {prop.id} with host {prop.host_name}")
                    else:
                        print(f"✗ Failed to fetch host for property {prop.id}")
                except Exception as e:
                    print(f"✗ Error for property {prop.id}: {e}")
        
        await session.commit()
        print("\n✓ Host data population complete!")


if __name__ == '__main__':
    asyncio.run(populate_host_data())