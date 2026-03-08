# ============================================================
# db/users.py
# All database operations for the users table
# Uses SQLAlchemy ORM
#
# Table:
#   users (id, email, password_hash, role, status, created_at)
# ============================================================

import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import User


def create_user(db: Session, email: str, password: str, role: str = "user") -> User:
    """
    Register a new user.
    - Hashes password with bcrypt before storing
    - Raises ValueError if email already exists
    """
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    user = User(email=email, password_hash=password_hash, role=role, status="active")
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Email already exists: {email}")


def login_user(db: Session, email: str, password: str) -> User | None:
    """
    Verify email + password.
    - Returns User on success
    - Returns None if email not found or password wrong
    - Raises PermissionError if user is banned or deleted
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if user.status == "banned":
        raise PermissionError("Your account has been banned.")

    if user.status == "deleted":
        raise PermissionError("Your account has been deleted.")

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None

    return user


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Fetch a single user by UUID. Returns None if not found."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a single user by email. Returns None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session) -> list[User]:
    """
    Fetch all users ordered by creation date.
    Admin only — do not expose to regular users.
    """
    return db.query(User).order_by(User.created_at.desc()).all()


def update_role(db: Session, user_id: str, new_role: str) -> bool:
    """
    Update a user's role.
    Allowed values: 'user', 'admin', 'superadmin'
    Note: always log this action in audit_logs after calling.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    user.role = new_role
    db.commit()
    return True


def update_status(db: Session, user_id: str, new_status: str) -> bool:
    """
    Update a user's status.
    Allowed values: 'active', 'banned', 'deleted'
    Note: 'deleted' is a soft delete — row is kept for audit purposes.
    Note: always log this action in audit_logs after calling.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    user.status = new_status
    db.commit()
    return True