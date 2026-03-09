import json
from typing import List

from fastapi import APIRouter, HTTPException, Request, status

from ag2.manager import run_stock_query
from app.dependencies import CurrentUser, DBSession
from app.schemas.api import ChatHistoryCreate, ChatHistoryResponse
from app.schemas.query_schemas import QueryResponse
from app.services.chat_history_service import ChatHistoryService
from caches.redis_client import (
    check_rate_limit,
    clear_session,
    get_cached,
    get_session,
    set_cache,
    set_session,
)

router = APIRouter(prefix="/chat", tags=["chat"])


def decimal_safe(obj):
    from datetime import date, datetime
    from decimal import Decimal

    if isinstance(obj, list):
        return [decimal_safe(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_safe(v) for k, v in obj.items()}
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


@router.post("/", response_model=QueryResponse)
async def process_chat(
    request: Request,
    chat_data: ChatHistoryCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    user_id = str(current_user.id)
    sid = chat_data.session_id or f"session_{user_id}"

    # Rate limiting
    rate = check_rate_limit(user_id, max_requests=10, window=60)
    if not rate["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded! Try again in {rate['reset_in']}s.",
        )

    chat_service = ChatHistoryService(db)
    new_question = chat_data.human_query.strip()

    if not new_question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Get context from Redis (for short-term session)
    history = get_session(sid)
    full_context = (
        "\n".join(history) + f"\nUser: {new_question}"
        if history
        else new_question
    )

    # Check cache
    cached_result = get_cached(full_context, sid)
    if cached_result:
        await chat_service.save_chat(
            user_id=user_id,
            human_query=new_question,
            sql_generated=cached_result.get("sql"),
            result_summary=json.dumps(cached_result.get("data"))
            if cached_result.get("data")
            else None,
        )
        return QueryResponse(
            **cached_result,
            session_id=sid,
            cached=True,
            remaining_requests=rate["remaining"],
        )

    try:
        # Run AG2 Query
        result = run_stock_query(full_context, human_input_mode="NEVER")
        result = decimal_safe(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result["status"] == "clarification_needed":
        # Save context to Redis for next turn
        history.append(f"User: {new_question}")
        history.append(f"Assistant: {result.get('question', '')}")
        set_session(sid, history)
    else:
        # Query successful or out of scope, clear session context and cache result
        clear_session(sid)
        if result["status"] == "answer":
            set_cache(full_context, sid, result, ttl=3600)
            await chat_service.save_chat(
                user_id=user_id,
                human_query=new_question,
                sql_generated=result.get("sql"),
                result_summary=json.dumps(result.get("data"))
                if result.get("data")
                else None,
            )

    return QueryResponse(
        status=result["status"],
        data=result.get("data"),
        message=result.get("message") or result.get("question"),
        session_id=sid,
        cached=False,
        remaining_requests=rate["remaining"],
    )


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    db: DBSession, current_user: CurrentUser, limit: int = 20
):
    chat_service = ChatHistoryService(db)
    history = await chat_service.get_user_chat_history(
        user_id=str(current_user.id), limit=limit
    )
    return history


@router.delete("/history", response_model=int)
async def delete_chat_history(db: DBSession, current_user: CurrentUser):
    chat_service = ChatHistoryService(db)
    count = await chat_service.delete_user_chat_history(
        user_id=str(current_user.id)
    )
    return count
