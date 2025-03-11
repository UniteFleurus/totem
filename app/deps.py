from fastapi import Depends, HTTPException, status
from typing import List, Callable
from app.db.models.user import User
from app.api.routers.auth import oauth2_scheme
import jwt
from app.config import settings


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    user = await User.get_or_none(username=username)
    if user is None:
        raise credentials_exception
    return user


def require_permissions(permissions: List[str]) -> Callable:
    async def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        for permission in permissions:
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission insuffisante. Requis: {permission}"
                )
        return current_user
    return permission_dependency
