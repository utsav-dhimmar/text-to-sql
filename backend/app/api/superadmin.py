from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentSuperAdminUser, DBSession
from app.schemas.api import UserAdminResponse, UserUpdateRole
from app.services.user_service import UserService

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.get("/admins", response_model=List[UserAdminResponse])
async def get_admins(db: DBSession, current_superadmin: CurrentSuperAdminUser):
    user_service = UserService(db)
    return await user_service.get_admins()


@router.patch("/users/{user_id}/role", response_model=bool)
async def update_user_role(
    user_id: UUID,
    role_data: UserUpdateRole,
    db: DBSession,
    current_superadmin: CurrentSuperAdminUser,
):
    if role_data.role == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin role is reserved.",
        )
    user_service = UserService(db)
    try:
        return await user_service.update_role(str(user_id), role_data.role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
