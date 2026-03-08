# ============================================================
# db/chat_history.py
# All database operations for the chat_history table
# Uses SQLAlchemy ORM
#
# Table:
#   chat_history (id, user_id, human_query, sql_generated,
#                 result_summary, created_at)
# ============================================================

from sqlalchemy.orm import Session
from db.models import ChatHistory


def save_chat(
    db:             Session,
    user_id:        str,
    human_query:    str,
    sql_generated:  str,
    result_summary: str,
) -> ChatHistory:
    """
    Save a chatbot question and its result.
    - user_id       : UUID of the user who asked
    - human_query   : the original question in plain English
    - sql_generated : the SQL that was executed
    - result_summary: the answer returned to the user
    """
    chat = ChatHistory(
        user_id=user_id,
        human_query=human_query,
        sql_generated=sql_generated,
        result_summary=result_summary,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_user_chat_history(db: Session, user_id: str, limit: int = 20) -> list[ChatHistory]:
    """
    Fetch chat history for a specific user.
    Returns most recent chats first.
    """
    return (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def get_recent_chats_for_context(db: Session, user_id: str, limit: int = 5) -> list[ChatHistory]:
    """
    Fetch the last N chats in chronological order.
    Used by AG2 agent to remember conversation context.
    """
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    # Reverse to get chronological order for context
    return list(reversed(chats))


def delete_user_chat_history(db: Session, user_id: str) -> int:
    """
    Delete all chat history for a user.
    Returns number of rows deleted.
    """
    count = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .delete()
    )
    db.commit()
    return count