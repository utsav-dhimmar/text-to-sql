from typing import Annotated
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from core.config import get_settings
from core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token_type,
)
from dependencies import CurrentUser, DBSession, UserServiceDep
from models.user import UserRole
from schemas.auth import (
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

# OAuth setup
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url=settings.GOOGLE_CONF_URL,
    client_kwargs={"scope": "openid email profile"},
)


@router.post(
    "/register",
    # ... rest of the file ...
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: DBSession,
    user_service: UserServiceDep,
):
    try:
        user = await user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            role=UserRole.USER.value,
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.value,
            status=user.status.value,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    user_service: UserServiceDep,
    response: Response,
):
    try:
        user = await user_service.login_user(
            email=credentials.email,
            password=credentials.password,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set cookies
    is_secure = settings.ENV != "development"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/google/login")
async def google_login(request: Request):
    """
    Redirect the user to Google for authentication.
    """
    redirect_uri = f"{request.base_url}api/auth/google/callback"
    # Ensure it's using https if in production (optional, depending on proxy)
    if settings.ENV != "development" and not str(redirect_uri).startswith("https"):
        redirect_uri = str(redirect_uri).replace("http://", "https://")

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    user_service: UserServiceDep,
):
    """
    Handle the callback from Google, exchange code for tokens, and log in the user.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}",
        )

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not fetch user info from Google",
        )

    google_id = user_info.get("sub")
    email = user_info.get("email")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incomplete user info from Google",
        )

    try:
        user = await user_service.get_or_create_google_user(
            google_id=google_id,
            email=email,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set cookies
    is_secure = settings.ENV != "development"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    # Redirect to frontend
    # In a real app, you might want to redirect to a specific success page or dashboard
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    user_service: UserServiceDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        payload = verify_token_type(refresh_token, expected_type="refresh")
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    # Update cookies
    is_secure = settings.ENV != "development"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: CurrentUser, response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return MessageResponse(message="Successfully logged out")
