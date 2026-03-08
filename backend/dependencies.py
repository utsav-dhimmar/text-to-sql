from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session_maker, get_db
from services.audit_log_service import AuditLogService
from services.chat_history_service import ChatHistoryService
from services.dataset_service import DatasetService
from services.user_service import UserService


DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(db: DBSession) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_chat_history_service(db: DBSession) -> ChatHistoryService:
    return ChatHistoryService(db)


ChatHistoryServiceDep = Annotated[ChatHistoryService, Depends(get_chat_history_service)]


def get_audit_log_service(db: DBSession) -> AuditLogService:
    return AuditLogService(db)


AuditLogServiceDep = Annotated[AuditLogService, Depends(get_audit_log_service)]


def get_dataset_service(db: DBSession) -> DatasetService:
    return DatasetService(db)


DatasetServiceDep = Annotated[DatasetService, Depends(get_dataset_service)]
