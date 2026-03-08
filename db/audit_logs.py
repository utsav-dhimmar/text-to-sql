# ============================================================
# db/audit_logs.py
# All database operations for the audit_logs table
#
# Table:
#   audit_logs (id, actor_id, action, target_id, created_at)
#
# Rules:
#   - Append only — never update or delete rows
#   - actor_id is required (who did the action)
#   - target_id is optional (which user was affected)
# ============================================================

import psycopg2
import psycopg2.extras
from db.connection import get_conn


# Common action constants — use these instead of raw strings
ACTION_ROLE_CHANGED   = "role_changed"
ACTION_USER_BANNED    = "user_banned"
ACTION_USER_UNBANNED  = "user_unbanned"
ACTION_USER_DELETED   = "user_deleted"
ACTION_DATASET_ADDED  = "dataset_added"
ACTION_DATASET_DELETED= "dataset_deleted"


def log_action(actor_id: str, action: str, target_id: str = None) -> dict:
    """
    Insert a new audit log entry.
    - actor_id : UUID of the user performing the action (required)
    - action   : string describing the action (use ACTION_* constants above)
    - target_id: UUID of the affected user (optional, pass None if not applicable)
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO audit_logs (actor_id, action, target_id)
            VALUES (%s, %s, %s)
            RETURNING id, actor_id, action, target_id, created_at
        """, (actor_id, action, target_id))
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_all_logs(limit: int = 50) -> list:
    """
    Fetch recent audit logs with actor and target email.
    Admin only — do not expose to regular users.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                al.id,
                al.action,
                al.created_at,
                actor.email  AS actor_email,
                target.email AS target_email
            FROM audit_logs al
            JOIN  users actor  ON actor.id  = al.actor_id
            LEFT JOIN users target ON target.id = al.target_id
            ORDER BY al.created_at DESC
            LIMIT %s
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_logs_by_actor(actor_id: str, limit: int = 50) -> list:
    """Fetch all actions performed by a specific user."""
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, action, target_id, created_at
            FROM audit_logs
            WHERE actor_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (actor_id, limit))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_logs_by_target(target_id: str, limit: int = 50) -> list:
    """Fetch all actions that affected a specific user."""
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, action, actor_id, created_at
            FROM audit_logs
            WHERE target_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (target_id, limit))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
