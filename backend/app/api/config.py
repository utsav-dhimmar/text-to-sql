
API_BASE = "https://ollama.com"
API_KEY  = "4463f73a63124d84b060905c4ff2a87e.gAiREoFjqQ86h9tcgbhVLt_v"
MODEL    = "glm-5:cloud"


DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "analytics_db",
    "user":     "postgres",
    "password": "root",
}


class Settings:
    FRONTEND_URL = "http://localhost:3000"


settings = Settings()
