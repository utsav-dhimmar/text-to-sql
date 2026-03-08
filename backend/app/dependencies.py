from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_token, oauth2_scheme
from app.db.database import get_db
from app.schemas.auth import UserResponse
from app.services.user_service import UserService

DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(db: DBSession) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> UserResponse:
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status.value == "banned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned",
        )

    if user.status.value == "deleted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deleted",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        status=user.status.value,
    )


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    return current_user


CurrentUser = Annotated[UserResponse, Depends(get_current_active_user)]


async def get_current_admin_user(
    current_user: CurrentUser,
) -> UserResponse:
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


CurrentAdminUser = Annotated[UserResponse, Depends(get_current_admin_user)]
