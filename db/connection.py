# ============================================================
# db/connection.py
# SQLAlchemy engine, session, and Base
# All db files import from here
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# ── Engine ───────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # auto-reconnect on lost connections
    pool_size=5,             # max 5 persistent connections
    max_overflow=10,         # max 10 extra connections under load
    echo=False,              # set True to log all SQL queries
)

# ── Session ──────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Base ─────────────────────────────────────────────────────
Base = declarative_base()


def get_db():
    """
    Dependency function — yields a DB session.
    Use this in FastAPI endpoints:

        from db.connection import get_db
        from sqlalchemy.orm import Session

        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()