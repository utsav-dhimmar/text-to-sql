from typing import List
from uuid import UUID

from fastapi import APIRouter

from app.dependencies import CurrentAdminUser, DBSession
from app.schemas.api import (
    AuditLogResponse,
    ChatHistoryResponse,
    UserAdminResponse,
    UserUpdateRole,
    UserUpdateStatus,
)
from app.services.audit_log_service import AuditLogService
from app.services.chat_history_service import ChatHistoryService
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserAdminResponse])
async def get_all_users(db: DBSession, current_admin: CurrentAdminUser):
    user_service = UserService(db)
    users = await user_service.get_all_users()
    return users


@router.delete("/users/{user_id}", response_model=bool)
async def delete_user(
    user_id: UUID, db: DBSession, current_admin: CurrentAdminUser
):
    user_service = UserService(db)
    audit_log_service = AuditLogService(db)

    success = await user_service.delete_user(str(user_id))
    if success:
        await audit_log_service.log_action(
            actor_id=current_admin.id,
            action=AuditLogService.ACTION_USER_DELETED,
            target_id=user_id,
        )
    return success


@router.patch("/users/{user_id}/status", response_model=bool)
async def update_user_status(
    user_id: UUID,
    status_data: UserUpdateStatus,
    db: DBSession,
    current_admin: CurrentAdminUser,
):
    user_service = UserService(db)
    audit_log_service = AuditLogService(db)

    success = await user_service.update_status(str(user_id), status_data.status)
    if success:
        action = (
            AuditLogService.ACTION_USER_BANNED
            if status_data.status == "banned"
            else AuditLogService.ACTION_USER_UNBANNED
        )
        await audit_log_service.log_action(
            actor_id=current_admin.id, action=action, target_id=user_id
        )
    return success


@router.patch("/users/{user_id}/role", response_model=bool)
async def update_user_role(
    user_id: UUID,
    role_data: UserUpdateRole,
    db: DBSession,
    current_admin: CurrentAdminUser,
):
    user_service = UserService(db)
    audit_log_service = AuditLogService(db)

    success = await user_service.update_role(str(user_id), role_data.role)
    if success:
        await audit_log_service.log_action(
            actor_id=current_admin.id,
            action=f"role_changed_to_{role_data.role}",
            target_id=user_id,
        )
    return success


@router.get("/chats", response_model=List[ChatHistoryResponse])
async def get_all_chats(
    db: DBSession, current_admin: CurrentAdminUser, limit: int = 100
):
    chat_service = ChatHistoryService(db)
    chats = await chat_service.get_all_chat_history(limit=limit)
    return chats


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    db: DBSession, current_admin: CurrentAdminUser, limit: int = 50
):
    audit_log_service = AuditLogService(db)
    logs = await audit_log_service.get_all_logs(limit=limit)
    return logs
