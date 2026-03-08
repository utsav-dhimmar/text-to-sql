import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import AuditLog


class AuditLogService:
    ACTION_ROLE_CHANGED = "role_changed"
    ACTION_USER_BANNED = "user_banned"
    ACTION_USER_UNBANNED = "user_unbanned"
    ACTION_USER_DELETED = "user_deleted"
    ACTION_DATASET_ADDED = "dataset_added"
    ACTION_DATASET_DELETED = "dataset_deleted"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self, actor_id: uuid.UUID, action: str, target_id: Optional[uuid.UUID] = None
    ) -> AuditLog:
        log = AuditLog(actor_id=actor_id, action=action, target_id=target_id)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_all_logs(self, limit: int = 50) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_logs_by_actor(
        self, actor_id: uuid.UUID, limit: int = 50
    ) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_logs_by_target(
        self, target_id: uuid.UUID, limit: int = 50
    ) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
