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


class AdminAnalyticsResponse(BaseModel):
    total_users: int
    active_users: int
    banned_users: int
    total_admins: int
    total_queries: int


class SectorCreate(BaseModel):
    sector_name: str


class CompanyCreate(BaseModel):
    company_name: str
    industry_id: int


class SectorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sector_id: int
    sector_name: str


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    company_id: int
    company_name: str
    industry_id: int
