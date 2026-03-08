# ============================================================
# config.py
# Central place for all environment variables
# All other files import from here — never use os.getenv directly
#
# Setup:
#   1. Copy .env.example to .env
#   2. Fill in your values
#   3. Never commit .env to GitHub
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()


# ── Database ─────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5433")
DB_NAME     = os.getenv("DB_NAME",     "nifty500")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# SQLAlchemy connection URL
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Redis ─────────────────────────────────────────────────────
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# ── OpenAI ───────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")