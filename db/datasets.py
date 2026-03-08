# ============================================================
# db/datasets.py
# All database operations for the datasets table
#
# Table:
#   datasets (id, name, source, uploaded_by, table_name,
#             row_count, status, created_at)
# ============================================================

import psycopg2
import psycopg2.extras
from db.connection import get_conn


# Status constants
STATUS_PROCESSING = "processing"
STATUS_READY      = "ready"
STATUS_ERROR      = "error"


def get_all_datasets() -> list:
    """
    Fetch all datasets with uploader email.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT
                d.id,
                d.name,
                d.source,
                d.table_name,
                d.row_count,
                d.status,
                d.created_at,
                u.email AS uploaded_by_email
            FROM datasets d
            LEFT JOIN users u ON u.id = d.uploaded_by
            ORDER BY d.created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_dataset_by_id(dataset_id: str) -> dict | None:
    """Fetch a single dataset by UUID. Returns None if not found."""
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT id, name, source, table_name, row_count, status, created_at
            FROM datasets
            WHERE id = %s
        """, (dataset_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        cur.close()
        conn.close()


def create_dataset(
    name:        str,
    table_name:  str,
    source:      str  = "manual upload",
    uploaded_by: str  = None,
    row_count:   int  = 0,
) -> dict:
    """
    Register a new dataset.
    Status starts as 'processing' automatically.
    """
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO datasets (name, source, uploaded_by, table_name, row_count, status)
            VALUES (%s, %s, %s, %s, %s, 'processing')
            RETURNING id, name, table_name, status, created_at
        """, (name, source, uploaded_by, table_name, row_count))
        row = dict(cur.fetchone())
        conn.commit()
        return row
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def update_status(dataset_id: str, status: str, row_count: int = None) -> bool:
    """
    Update dataset status.
    Allowed values: 'processing', 'ready', 'error'
    Optionally update row_count when marking as ready.
    """
    conn = get_conn()
    cur  = conn.cursor()
    try:
        if row_count is not None:
            cur.execute("""
                UPDATE datasets SET status = %s, row_count = %s WHERE id = %s
            """, (status, row_count, dataset_id))
        else:
            cur.execute("""
                UPDATE datasets SET status = %s WHERE id = %s
            """, (status, dataset_id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def delete_dataset(dataset_id: str) -> bool:
    """
    Delete a dataset record.
    Note: this does NOT drop the actual SQL table — handle that separately.
    """
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("DELETE FROM datasets WHERE id = %s", (dataset_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
