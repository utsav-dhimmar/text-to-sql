from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.dependencies import CurrentUser, DBSession
from app.schemas.api import ChatHistoryCreate, ChatHistoryResponse
from app.services.chat_history_service import ChatHistoryService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatHistoryResponse)
async def save_chat(
    chat_data: ChatHistoryCreate,
    db: DBSession,
    current_user: CurrentUser
):
    chat_service = ChatHistoryService(db)
    chat = await chat_service.save_chat(
        user_id=str(current_user.id),
        human_query=chat_data.human_query,
        sql_generated=chat_data.sql_generated,
        result_summary=chat_data.result_summary
    )
    return chat

@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    db: DBSession,
    current_user: CurrentUser,
    limit: int = 20
):
    chat_service = ChatHistoryService(db)
    history = await chat_service.get_user_chat_history(
        user_id=str(current_user.id),
        limit=limit
    )
    return history

@router.delete("/history", response_model=int)
async def delete_chat_history(
    db: DBSession,
    current_user: CurrentUser
):
    chat_service = ChatHistoryService(db)
    count = await chat_service.delete_user_chat_history(user_id=str(current_user.id))
    return count
