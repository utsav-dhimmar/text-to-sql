from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    role: str
    status: str
    created_at: datetime


class UserUpdateStatus(BaseModel):
    status: str


class UserUpdateRole(BaseModel):
    role: str


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor_id: UUID
    action: str
    target_id: Optional[UUID] = None
    created_at: datetime


class ChatHistoryCreate(BaseModel):
    human_query: str
    session_id: Optional[str] = None
    sql_generated: Optional[str] = None
    result_summary: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    human_query: str
    sql_generated: Optional[str] = None
    result_summary: Optional[str] = None
    created_at: datetime


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    source: str
    table_name: str
    row_count: int
    status: str
    uploaded_by: Optional[UUID] = None
    created_at: datetime
