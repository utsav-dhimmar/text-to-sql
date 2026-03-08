# ============================================================
# db/chat_history.py
# All database operations for the chat_history table
#
# Table:
#   chat_history (id, user_id, human_query, sql_generated,
#                 result_summary, created_at)
# ============================================================

import psycopg2
import psycopg2.extras
from db.connection import get_conn


def save_chat(
    user_id:        str,
    human_query:    str,
    sql_generated:  str,
    result_summary: str,
) -> dict:
    """
    Save a chatbot question and its result.
    - user_id       : UUID of the user who asked
    - human_query   : the original question in plain English
    - sql_generated : the SQL that was executed
    - result_summary: the answer returned to the user
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO chat_history
                (user_id, human_query, sql_generated, result_summary)
            VALUES (%s, %s, %s, %s)
            RETURNING id, created_at
        """, (user_id, human_query, sql_generated, result_summary))
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_user_chat_history(user_id: str, limit: int = 20) -> list:
    """
    Fetch chat history for a specific user.
    Returns most recent chats first.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, human_query, sql_generated, result_summary, created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_recent_chats_for_context(user_id: str, limit: int = 5) -> list:
    """
    Fetch the last N chats in chronological order.
    Used by AG2 agent to remember conversation context.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT human_query, result_summary, created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        rows = [dict(r) for r in cur.fetchall()]
        # Reverse to get chronological order for context
        return list(reversed(rows))
    finally:
        cur.close()
        conn.close()


def delete_user_chat_history(user_id: str) -> int:
    """
    Delete all chat history for a user.
    Returns number of rows deleted.
    """
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM chat_history WHERE user_id = %s
        """, (user_id,))
        count = cur.rowcount
        conn.commit()
        return count
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
