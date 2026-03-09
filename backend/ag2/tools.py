"""
ag2/tools.py — SQLAlchemy-based DB tools for AG2 agents
All queries run through the synchronous SQLAlchemy engine.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rapidfuzz import process, fuzz
from sqlalchemy import text

from app.db.database import SyncSessionLocal


def find_company(name: str) -> dict:
    """Search by company name OR NSE/BSE code (e.g. 'TCS', 'INFY')"""
    with SyncSessionLocal() as session:
        # Fetch all companies
        rows = session.execute(
            text("SELECT company_id, company_name FROM companies")
        ).fetchall()

    all_companies = {row.company_name: row.company_id for row in rows}
    names_list = list(all_companies.keys())

    # 1. Exact company name match
    for n in names_list:
        if n.lower() == name.lower():
            return {
                "found": True, "exact": True, "company_name": n,
                "company_id": all_companies[n], "suggestions": [],
            }

    # 2. NSE/BSE code match — "TCS" → "Tata Consultancy Services Ltd."
    with SyncSessionLocal() as session:
        code_row = session.execute(
            text("""
                SELECT c.company_name, c.company_id
                FROM exchange_listings el
                JOIN companies c ON c.company_id = el.company_id
                WHERE UPPER(el.code) = UPPER(:code)
                LIMIT 1
            """),
            {"code": name},
        ).fetchone()

    if code_row:
        return {
            "found": True, "exact": True, "company_name": code_row.company_name,
            "company_id": code_row.company_id, "suggestions": [],
        }

    # 3. Partial name match
    name_lower = name.lower()
    partial = [n for n in names_list if name_lower in n.lower()]
    if partial:
        return {
            "found": True, "exact": False, "company_name": partial[0],
            "company_id": all_companies[partial[0]], "suggestions": partial[:5],
        }

    # 4. Fuzzy fallback — multiple scorers
    from rapidfuzz import process as rprocess

    matches1 = rprocess.extract(name, names_list, scorer=fuzz.WRatio, limit=5)
    matches2 = rprocess.extract(name, names_list, scorer=fuzz.partial_ratio, limit=5)
    matches3 = rprocess.extract(name, names_list, scorer=fuzz.token_sort_ratio, limit=5)

    # Combine scores
    score_map = {}
    for m in matches1 + matches2 + matches3:
        cname, score = m[0], m[1]
        if cname not in score_map or score > score_map[cname]:
            score_map[cname] = score

    suggestions = [
        k for k, v in sorted(score_map.items(), key=lambda x: -x[1]) if v > 60
    ][:5]

    if suggestions:
        return {
            "found": True, "exact": False, "company_name": suggestions[0],
            "company_id": all_companies[suggestions[0]], "suggestions": suggestions,
        }

    return {
        "found": False, "exact": False, "company_name": None,
        "company_id": None, "suggestions": [],
    }


def get_quarters() -> list:
    with SyncSessionLocal() as session:
        rows = session.execute(
            text("SELECT DISTINCT quarter FROM quarterly_results ORDER BY quarter")
        ).fetchall()
    return [r.quarter for r in rows]


def get_sectors() -> list:
    with SyncSessionLocal() as session:
        rows = session.execute(
            text("SELECT sector_name FROM sectors ORDER BY sector_name")
        ).fetchall()
    return [r.sector_name for r in rows]


def run_query(sql: str) -> list:
    """Execute an LLM-generated SQL query via SQLAlchemy and return results as list of dicts."""
    with SyncSessionLocal() as session:
        try:
            result = session.execute(text(sql))
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            return [{"error": str(e)}]


def get_schema_info() -> str:
    return """
PostgreSQL Schema:
- companies(company_id, company_name, industry_id)
- sectors(sector_id, sector_name)
- industries(industry_id, industry_name, sector_id)
- exchange_listings(listing_id, company_id, exchange, code)  -- NSE/BSE codes
- company_financials(result_id, company_id, quarter, period_end_date,
    revenue, operating_expenses, operating_profit, operating_profit_margin,
    depreciation, interest, profit_before_tax, tax, net_profit, eps, profit_ttm, eps_ttm)
All financial values in INR Crores. operating_profit_margin is a number (18.48 = 18.48%).
"""