# ============================================================
# auth.py — Auth & Database Operations
# Handles: users, audit_logs, chat_history, datasets
#
# Install:
#   pip install psycopg2-binary bcrypt python-dotenv
# ============================================================

import os

import bcrypt
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# ── DB Connection ─────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "nifty500"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

print(
    "Connecting with:",
    DB_CONFIG["host"],
    DB_CONFIG["database"],
    DB_CONFIG["user"],
    DB_CONFIG["password"],
)


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# USERS
# ============================================================


def create_user(email: str, password: str, role: str = "user") -> dict:
    """
    Register a new user.
    Password is hashed with bcrypt before storing.
    """
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            INSERT INTO users (email, password_hash, role, status)
            VALUES (%s, %s, %s, 'active')
            RETURNING id, email, role, status, created_at
        """,
            (email, password_hash, role),
        )
        user = dict(cur.fetchone())
        conn.commit()
        print(f"✅ User created: {email}")
        return user
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError(f"Email already exists: {email}")
    finally:
        cur.close()
        conn.close()


def login_user(email: str, password: str) -> dict | None:
    """
    Verify email + password.
    Returns user dict if valid, None if invalid.
    """
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, email, password_hash, role, status
            FROM users
            WHERE email = %s
        """,
            (email,),
        )
        user = cur.fetchone()

        if not user:
            print("❌ User not found")
            return None

        if user["status"] == "banned":
            print("❌ User is banned")
            return None

        if user["status"] == "deleted":
            print("❌ User account deleted")
            return None

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            print("❌ Wrong password")
            return None

        print(f"✅ Login successful: {email}")
        return {
            "id": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
        }
    finally:
        cur.close()
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a single user by UUID."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, email, role, status, created_at
            FROM users WHERE id = %s
        """,
            (user_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()


def get_all_users() -> list:
    """Fetch all users — admin only."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, role, status, created_at
            FROM users ORDER BY created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def update_user_role(actor_id: str, target_id: str, new_role: str) -> bool:
    """
    Change a user's role.
    Automatically logs to audit_logs.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE users SET role = %s WHERE id = %s
        """,
            (new_role, target_id),
        )

        # Log to audit_logs
        cur.execute(
            """
            INSERT INTO audit_logs (actor_id, action, target_id)
            VALUES (%s, %s, %s)
        """,
            (actor_id, f"role_changed_to_{new_role}", target_id),
        )

        conn.commit()
        print(f"✅ Role updated to {new_role}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def update_user_status(actor_id: str, target_id: str, new_status: str) -> bool:
    """
    Ban, unban or soft-delete a user.
    Automatically logs to audit_logs.
    """
    action_map = {
        "banned": "user_banned",
        "active": "user_unbanned",
        "deleted": "user_deleted",
    }
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE users SET status = %s WHERE id = %s
        """,
            (new_status, target_id),
        )

        cur.execute(
            """
            INSERT INTO audit_logs (actor_id, action, target_id)
            VALUES (%s, %s, %s)
        """,
            (actor_id, action_map.get(new_status, new_status), target_id),
        )

        conn.commit()
        print(f"✅ Status updated to {new_status}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()


# ============================================================
# AUDIT LOGS
# ============================================================


def log_action(actor_id: str, action: str, target_id: str = None):
    """Log any admin action to audit_logs."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO audit_logs (actor_id, action, target_id)
            VALUES (%s, %s, %s)
        """,
            (actor_id, action, target_id),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_audit_logs(limit: int = 50) -> list:
    """Fetch recent audit logs — admin only."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT
                al.id,
                al.action,
                al.created_at,
                actor.email AS actor_email,
                target.email AS target_email
            FROM audit_logs al
            JOIN users actor  ON actor.id  = al.actor_id
            LEFT JOIN users target ON target.id = al.target_id
            ORDER BY al.created_at DESC
            LIMIT %s
        """,
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


# ============================================================
# CHAT HISTORY
# ============================================================


def save_chat(
    user_id: str, human_query: str, sql_generated: str, result_summary: str
) -> dict:
    """Save a chatbot question and its result."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            INSERT INTO chat_history (user_id, human_query, sql_generated, result_summary)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """,
            (user_id, human_query, sql_generated, result_summary),
        )
        row = dict(cur.fetchone())
        conn.commit()
        return row
    finally:
        cur.close()
        conn.close()


def get_user_chat_history(user_id: str, limit: int = 20) -> list:
    """Fetch chat history for a specific user."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT id, human_query, sql_generated, result_summary, created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """,
            (user_id, limit),
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_recent_chats_for_context(user_id: str, limit: int = 5) -> list:
    """
    Get last N chat messages for conversation context.
    Used by AG2 to remember what was previously discussed.
    """
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """
            SELECT human_query, result_summary, created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """,
            (user_id, limit),
        )
        rows = [dict(r) for r in cur.fetchall()]
        # Return in chronological order for context
        return list(reversed(rows))
    finally:
        cur.close()
        conn.close()


# ============================================================
# DATASETS
# ============================================================


def get_all_datasets() -> list:
    """Fetch all registered datasets."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT d.id, d.name, d.source, d.table_name,
                   d.row_count, d.status, d.created_at,
                   u.email AS uploaded_by_email
            FROM datasets d
            LEFT JOIN users u ON u.id = d.uploaded_by
            ORDER BY d.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def update_dataset_status(dataset_id: str, status: str):
    """Update dataset processing status."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE datasets SET status = %s WHERE id = %s
        """,
            (status, dataset_id),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  Auth Script — Test Run")
    print("=" * 50)

    # 1. Create a test user
    print("\n── Test 1: Create user ─────────────────")
    try:
        user = create_user("test@example.com", "password123", "user")
        print(f"   Created: {user}")
        user_id = str(user["id"])
    except ValueError:
        print("   Already exists — fetching instead")
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id FROM users WHERE email = 'test@example.com'")
        user_id = str(cur.fetchone()["id"])
        cur.close()
        conn.close()

    # 2. Login
    print("\n── Test 2: Login ───────────────────────")
    result = login_user("test@example.com", "password123")
    print(f"   Login result: {result}")

    # 3. Save a chat
    print("\n── Test 3: Save chat ───────────────────")
    chat = save_chat(
        user_id,
        "Show me top 5 companies by revenue in Q1",
        "SELECT company_name, revenue FROM company_financials WHERE quarter = 'Q1 FY2025' ORDER BY revenue DESC LIMIT 5",
        "Top 5 companies: Reliance, TCS, HDFC Bank, Infosys, ICICI Bank",
    )
    print(f"   Saved chat: {chat}")

    # 4. Get chat history
    print("\n── Test 4: Get chat history ────────────")
    history = get_user_chat_history(user_id)
    print(f"   Found {len(history)} chats")

    # 5. Get audit logs
    print("\n── Test 5: Audit logs ──────────────────")
    logs = get_audit_logs(10)
    print(f"   Found {len(logs)} audit logs")

    print("\n" + "=" * 50)
    print("  ✅ All tests passed!")
    print("=" * 50)
