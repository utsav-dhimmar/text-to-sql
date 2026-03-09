"""
models/schemas.py — Pydantic request/response schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class QueryRequest(BaseModel):
    question:   str
    session_id: str
    user_id:    Optional[str] = "guest"   # Utsav ka JWT aane pe replace hoga


class QueryResponse(BaseModel):
    status:     str                        # "answer" | "clarification_needed" | "out_of_scope" | "error"
    data:       Optional[List[Any]] = None # Raw DB rows
    message:    Optional[str] = None       # clarification question / error message
    session_id: str
    cached:     bool = False
    remaining_requests: Optional[int] = None


class CompanySearchResponse(BaseModel):
    found:        bool
    exact:        bool
    company_name: Optional[str] = None
    company_id:   Optional[int] = None
    suggestions:  list = []