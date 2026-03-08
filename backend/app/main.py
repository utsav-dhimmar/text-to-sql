from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .api.auth import router as auth_router
from .api.query import router as query_router
from .core.config import get_settings
from .db.database import engine
from .models import Base

app = FastAPI(title="Text-to-SQL API", version="1.0.0")
settings = get_settings()


# Session middleware for OAuth state
app.add_middleware(
    SessionMiddleware,  # ty:ignore[invalid-argument-type]
    secret_key=settings.SESSION_SECRET,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth middleware to prevent guest access to specific routes
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # on below path user need to be required
    protected_paths = ["/api/auth/logout", "/api/auth/refresh", "/api/auth/me"]

    path = request.url.path.rstrip("/")
    # remove / from current path
    if path in protected_paths:
        # check token must be in cookie
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        auth_header = request.headers.get("Authorization")
        # no not allow
        if not (access_token or refresh_token or auth_header):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
            )

    # their is token allow user
    return await call_next(request)


@app.on_event("startup")
async def startup():
    # This ensures all tables are created if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth_router, prefix="/api")
app.include_router(query_router)


@app.get("/")
def sayHi():
    return {"message": "Hello world"}
