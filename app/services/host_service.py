"""Service to fetch host information from auth service."""
import httpx
from typing import Optional, Dict
from uuid import UUID
from app.config import settings


class HostService:
    """Service for fetching host information from auth service."""
    
    @staticmethod
    async def get_host_info(host_id: UUID) -> Optional[Dict]:
        """
        Fetch host information from auth service.
        Returns dict with id, name, email, avatar_url or None if not found.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/profiles/hosts/{host_id}/",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    host_data = response.json()
                    return {
                        "id": host_data.get("id"),
                        "name": f"{host_data.user_info.get('first_name', '')} {host_data.user_info.get('last_name', '')}".strip() or "Host",
                        "email": host_data.user_info.get("email", ""),
                        "avatar": host_data.user_info.get("avatar")
                    }
                return None
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to fetch host info for {host_id}: {str(e)}")
            return None
    
    @staticmethod
    async def get_multiple_hosts_info(host_ids: list[UUID]) -> Dict[UUID, Dict]:
        """
        Fetch multiple hosts information in batch.
        Returns dict mapping host_id to host info.
        """
        hosts_info = {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try batch endpoint if available
                response = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/api/profiles/hosts/",
                    json={"host_ids": [str(hid) for hid in host_ids]},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    batch_data = response.json()
                    print("batch_data =================================")
                    print(batch_data)
                    for host_data in batch_data:
                        host_id = UUID(host_data.get("id"))
                        user_info = host_data.get("user_info")
                        hosts_info[host_id] = {
                            "id": host_id,
                            "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or "Host",
                            "email": user_info.get("email", ""),
                            "avatar": user_info.get("avatar")
                        }
                else:
                    # Fallback: fetch individually
                    for host_id in host_ids:
                        host_info = await HostService.get_host_info(host_id)
                        if host_info:
                            hosts_info[host_id] = host_info
        except Exception as e:
            print(f"Failed to fetch batch host info: {str(e)}")
            # Fallback: fetch individually
            for host_id in host_ids:
                host_info = await HostService.get_host_info(host_id)
                if host_info:
                    hosts_info[host_id] = host_info
        
        return hosts_info
    
    