from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from typing import Optional
import httpx
from app.config import settings
from app.database import get_db
from app.schemas.common import UserInfo


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInfo:
    """
    Validate JWT token with Django auth service and return user info.
    """
    token = credentials.credentials
    
    # Verify token with Django auth service
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/me/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_data = response.json()
            
            # Map Django user response to UserInfo
            return UserInfo(
                id=user_data.get("id"),
                email=user_data.get("email"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                is_active=user_data.get("is_active", True),
                is_verified=user_data.get("is_verified", False)
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    """
    Ensure the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[UserInfo]:
    """
    Optional authentication - returns user if token is provided and valid, None otherwise.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


class PaginationParams:
    """Pagination query parameters."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
    
    @property
    def limit(self) -> int:
        return self.page_size