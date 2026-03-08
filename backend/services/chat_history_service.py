from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import ChatHistory


class ChatHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_chat(
        self,
        user_id: str,
        human_query: str,
        sql_generated: str,
        result_summary: str,
    ) -> ChatHistory:
        chat = ChatHistory(
            user_id=user_id,
            human_query=human_query,
            sql_generated=sql_generated,
            result_summary=result_summary,
        )
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_user_chat_history(
        self, user_id: str, limit: int = 20
    ) -> list[ChatHistory]:
        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_chats_for_context(
        self, user_id: str, limit: int = 5
    ) -> list[ChatHistory]:
        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        chats = list(result.scalars().all())
        return list(reversed(chats))

    async def delete_user_chat_history(self, user_id: str) -> int:
        result = await self.db.execute(
            select(ChatHistory).where(ChatHistory.user_id == user_id)
        )
        chats = result.scalars().all()
        count = len(chats)
        for chat in chats:
            await self.db.delete(chat)
        await self.db.commit()
        return count
