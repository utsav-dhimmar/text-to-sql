# ============================================================
# db/users.py
# All database operations for the users table
#
# Table:
#   users (id, email, password_hash, role, status, created_at)
# ============================================================

import bcrypt
import psycopg2
import psycopg2.extras
from db.connection import get_conn


def create_user(email: str, password: str, role: str = "user") -> dict:
    """
    Register a new user.
    - Hashes password with bcrypt before storing
    - Returns the created user (without password_hash)
    - Raises ValueError if email already exists
    """
    password_hash = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(12)
    ).decode()

    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO users (email, password_hash, role, status)
            VALUES (%s, %s, %s, 'active')
            RETURNING id, email, role, status, created_at
        """, (email, password_hash, role))
        user = dict(cur.fetchone())
        conn.commit()
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
    - Returns user dict on success
    - Returns None if email not found or password wrong
    - Raises PermissionError if user is banned or deleted
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, password_hash, role, status
            FROM users
            WHERE email = %s
        """, (email,))
        user = cur.fetchone()

        if not user:
            return None

        if user["status"] == "banned":
            raise PermissionError("Your account has been banned.")

        if user["status"] == "deleted":
            raise PermissionError("Your account has been deleted.")

        if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            return None

        return {
            "id":    str(user["id"]),
            "email": user["email"],
            "role":  user["role"],
        }
    finally:
        cur.close()
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    """Fetch a single user by UUID. Returns None if not found."""
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, role, status, created_at
            FROM users
            WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Fetch a single user by email. Returns None if not found."""
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, role, status, created_at
            FROM users
            WHERE email = %s
        """, (email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()


def get_all_users() -> list:
    """
    Fetch all users ordered by creation date.
    Admin only — do not expose to regular users.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, role, status, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def update_role(user_id: str, new_role: str) -> bool:
    """
    Update a user's role.
    Allowed values: 'user', 'admin', 'superadmin'
    Note: always log this action in audit_logs after calling.
    """
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            UPDATE users SET role = %s WHERE id = %s
        """, (new_role, user_id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def update_status(user_id: str, new_status: str) -> bool:
    """
    Update a user's status.
    Allowed values: 'active', 'banned', 'deleted'
    Note: 'deleted' is a soft delete — row is kept for audit purposes.
    Note: always log this action in audit_logs after calling.
    """
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            UPDATE users SET status = %s WHERE id = %s
        """, (new_status, user_id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
