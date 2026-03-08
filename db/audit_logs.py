# ============================================================
# db/audit_logs.py
# All database operations for the audit_logs table
# Uses SQLAlchemy ORM
#
# Table:
#   audit_logs (id, actor_id, action, target_id, created_at)
#
# Rules:
#   - Append only — never update or delete rows
#   - actor_id is required (who did the action)
#   - target_id is optional (which user was affected)
# ============================================================

from sqlalchemy.orm import Session
from db.models import AuditLog


# ── Action Constants ─────────────────────────────────────────
ACTION_ROLE_CHANGED    = "role_changed"
ACTION_USER_BANNED     = "user_banned"
ACTION_USER_UNBANNED   = "user_unbanned"
ACTION_USER_DELETED    = "user_deleted"
ACTION_DATASET_ADDED   = "dataset_added"
ACTION_DATASET_DELETED = "dataset_deleted"


def log_action(db: Session, actor_id: str, action: str, target_id: str = None) -> AuditLog:
    """
    Insert a new audit log entry.
    - actor_id : UUID of the user performing the action (required)
    - action   : string describing the action (use ACTION_* constants above)
    - target_id: UUID of the affected user (optional)
    """
    log = AuditLog(actor_id=actor_id, action=action, target_id=target_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_all_logs(db: Session, limit: int = 50) -> list[AuditLog]:
    """
    Fetch recent audit logs.
    Admin only — do not expose to regular users.
    """
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_logs_by_actor(db: Session, actor_id: str, limit: int = 50) -> list[AuditLog]:
    """Fetch all actions performed by a specific user."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.actor_id == actor_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_logs_by_target(db: Session, target_id: str, limit: int = 50) -> list[AuditLog]:
    """Fetch all actions that affected a specific user."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.target_id == target_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )