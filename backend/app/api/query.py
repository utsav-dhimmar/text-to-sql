"""
api/query.py — Stock market query routes
Raw DB data return — no markdown formatting
JWT: OFF (testing ke liye)
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from decimal import Decimal
from datetime import date, datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.query_schemas import QueryRequest, QueryResponse, CompanySearchResponse
from ag2.manager import run_stock_query
from ag2.tools import get_quarters, get_sectors, find_company
from caches.redis_client import (
    ping, get_cached, set_cache,
    get_session, set_session, clear_session,
    check_rate_limit
)
from app.db.database import get_db
from app.models.user import ChatHistory

router = APIRouter(prefix="/api", tags=["Stock Market"])


def decimal_safe(obj):
    if isinstance(obj, list):
        return [decimal_safe(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_safe(v) for k, v in obj.items()}
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


@router.post("/query", response_model=QueryResponse)
async def query_stocks(
    request: Request,
    body: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question empty hai.")

    user_id = body.user_id or request.client.host
    rate = check_rate_limit(user_id, max_requests=10, window=60)
    if not rate["allowed"]:
        raise HTTPException(status_code=429, detail=f"Rate limit exceed! {rate['reset_in']}s mein try karo.")

    sid          = body.session_id
    new_question = body.question.strip()
    history      = get_session(sid)
    full_context = "\n".join(history) + f"\nUser: {new_question}" if history else new_question

    async def save_to_db(sql_text, data_res):
        if body.user_id:
            try:
                uid = uuid.UUID(body.user_id)
                chat_record = ChatHistory(
                    user_id=uid,
                    human_query=body.question,
                    sql_generated=sql_text,
                    result_summary=str(data_res) if data_res else None
                )
                db.add(chat_record)
                await db.commit()
            except ValueError:
                pass


    cached_result = get_cached(full_context, sid)
    if cached_result:
        await save_to_db(cached_result.get("sql"), cached_result.get("data"))
        return QueryResponse(**cached_result, session_id=sid, cached=True, remaining_requests=rate["remaining"])

    try:
        result = run_stock_query(full_context, human_input_mode="NEVER")
        result = decimal_safe(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if result["status"] == "clarification_needed":
        history.append(f"User: {new_question}")
        history.append(f"Assistant: {result.get('question', '')}")
        set_session(sid, history)
    else:
        clear_session(sid)
        set_cache(full_context, sid, result, ttl=3600)
        await save_to_db(result.get("sql"), result.get("data"))

    return QueryResponse(
        status=result["status"],
        data=result.get("data"),
        message=result.get("message") or result.get("question"),
        session_id=sid,
        cached=False,
        remaining_requests=rate["remaining"]
    )


@router.get("/quarters")
async def list_quarters():
    return {"quarters": get_quarters()}


@router.get("/sectors")
async def list_sectors():
    return {"sectors": get_sectors()}


@router.get("/companies/search", response_model=CompanySearchResponse)
async def search_company(name: str):
    return find_company(name)


@router.get("/health")
async def health():
    return {"status": "ok", "redis": "connected" if ping() else "disconnected"}
