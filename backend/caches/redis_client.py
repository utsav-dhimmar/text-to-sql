"""
caches/redis_client.py — Redis connection + helpers
"""
import redis
import json
import hashlib
from decimal import Decimal
from datetime import date, datetime


class SafeEncoder(json.JSONEncoder):
    """Handle Decimal and date types for JSON serialization."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


# Redis connection
_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def ping() -> bool:
    try:
        return _client.ping()
    except Exception:
        return False


# ── Cache ────────────────────────────────────────────────────
def _cache_key(question: str, session_id: str) -> str:
    h = hashlib.md5(f"{question.lower().strip()}:{session_id}".encode()).hexdigest()[:16]
    return f"cache:query:{h}"

def get_cached(question: str, session_id: str):
    val = _client.get(_cache_key(question, session_id))
    return json.loads(val) if val else None

def set_cache(question: str, session_id: str, result: dict, ttl: int = 3600):
    _client.setex(_cache_key(question, session_id), ttl, json.dumps(result, cls=SafeEncoder))

def invalidate_cache(question: str, session_id: str):
    _client.delete(_cache_key(question, session_id))


# ── Session ──────────────────────────────────────────────────
def get_session(session_id: str) -> list:
    val = _client.get(f"session:{session_id}")
    return json.loads(val) if val else []

def set_session(session_id: str, history: list, ttl: int = 3600):
    _client.setex(f"session:{session_id}", ttl, json.dumps(history))

def clear_session(session_id: str):
    _client.delete(f"session:{session_id}")


# ── JWT Blacklist (Utsav ka auth aane pe) ───────────────────
def blacklist_token(jti: str, ttl: int):
    _client.setex(f"blacklist:{jti}", ttl, "")

def is_token_blacklisted(jti: str) -> bool:
    return _client.exists(f"blacklist:{jti}") > 0


# ── Rate Limiting ────────────────────────────────────────────
def check_rate_limit(identifier: str, max_requests: int = 10, window: int = 60) -> dict:
    key     = f"ratelimit:{identifier}"
    current = _client.get(key)

    if current is None:
        _client.setex(key, window, 1)
        return {"allowed": True, "remaining": max_requests - 1, "reset_in": window}

    count = int(current)
    ttl   = _client.ttl(key)

    if count >= max_requests:
        return {"allowed": False, "remaining": 0, "reset_in": ttl}

    _client.incr(key)
    return {"allowed": True, "remaining": max_requests - count - 1, "reset_in": ttl}