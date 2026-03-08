# ============================================================
# db/connection.py
# Single database connection used by all schema files
# ============================================================

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     os.getenv("DB_PORT",     "5432"),
    "database": os.getenv("DB_NAME",     "nifty500"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_conn():
    """Returns a new PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)
