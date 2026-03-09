"""
ag2/tools.py - Fixed: NSE/BSE code search + better fuzzy match
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2, psycopg2.extras
from rapidfuzz import process, fuzz
from app.api.config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def find_company(name: str) -> dict:
    """Search by company name OR NSE/BSE code (e.g. 'TCS', 'INFY')"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT company_id, company_name FROM companies")
    rows = cur.fetchall()
    cur.close();
    conn.close()

    all_companies = {row[1]: row[0] for row in rows}
    names_list = list(all_companies.keys())

    # 1. Exact company name match
    for n in names_list:
        if n.lower() == name.lower():
            return {"found": True, "exact": True, "company_name": n,
                    "company_id": all_companies[n], "suggestions": []}

    # 2. NSE/BSE code match — "TCS" → "Tata Consultancy Services Ltd."
    conn2 = get_connection()
    cur2 = conn2.cursor()
    cur2.execute("""
        SELECT c.company_name, c.company_id
        FROM exchange_listings el
        JOIN companies c ON c.company_id = el.company_id
        WHERE UPPER(el.code) = UPPER(%s)
        LIMIT 1
    """, (name,))
    code_row = cur2.fetchone()
    cur2.close();
    conn2.close()

    if code_row:
        return {"found": True, "exact": True, "company_name": code_row[0],
                "company_id": code_row[1], "suggestions": []}

    # 3. Partial name match
    name_lower = name.lower()
    partial = [n for n in names_list if name_lower in n.lower()]
    if partial:
        return {"found": True, "exact": False, "company_name": partial[0],
                "company_id": all_companies[partial[0]], "suggestions": partial[:5]}

    # 4. Fuzzy fallback — multiple scorers combine karo
    from rapidfuzz import process as rprocess

    # WRatio score
    matches1 = rprocess.extract(name, names_list, scorer=fuzz.WRatio, limit=5)
    # Partial ratio — "relayance" vs "Reliance Industries Ltd."
    matches2 = rprocess.extract(name, names_list, scorer=fuzz.partial_ratio, limit=5)
    # Token sort — word order different ho toh bhi match
    matches3 = rprocess.extract(name, names_list, scorer=fuzz.token_sort_ratio, limit=5)

    # Combine scores
    score_map = {}
    for m in matches1 + matches2 + matches3:
        cname, score = m[0], m[1]
        if cname not in score_map or score > score_map[cname]:
            score_map[cname] = score

    # Threshold 60 — typos handle karo
    suggestions = [k for k, v in sorted(score_map.items(), key=lambda x: -x[1]) if v > 60][:5]

    if suggestions:
        return {"found": True, "exact": False, "company_name": suggestions[0],
                "company_id": all_companies[suggestions[0]], "suggestions": suggestions}

    return {"found": False, "exact": False, "company_name": None,
            "company_id": None, "suggestions": []}


def get_quarters() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT quarter FROM quarterly_results ORDER BY quarter")
    rows = cur.fetchall();
    cur.close();
    conn.close()
    return [r[0] for r in rows]


def get_sectors() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT sector_name FROM sectors ORDER BY sector_name")
    rows = cur.fetchall();
    cur.close();
    conn.close()
    return [r[0] for r in rows]


def run_query(sql: str) -> list:
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(sql)
        return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        cur.close();
        conn.close()


def get_schema_info() -> str:
    return """
PostgreSQL Schema:
- companies(company_id, company_name, industry_id)
- sectors(sector_id, sector_name)
- industries(industry_id, industry_name, sector_id)
- exchange_listings(listing_id, company_id, exchange, code)  -- NSE/BSE codes
- quarterly_results(result_id, company_id, quarter, period_end_date,
    revenue, operating_expenses, operating_profit, operating_profit_margin,
    depreciation, interest, profit_before_tax, tax, net_profit, eps, profit_ttm, eps_ttm)
All financial values in INR Crores. operating_profit_margin is a number (18.48 = 18.48%).
"""