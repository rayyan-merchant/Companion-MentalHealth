from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import (
    AuthResponse,
    ChangePasswordRequest,
    CurrentAuth,
    UserCreate,
    UserLogin,
    UserResponse,
    authenticate_user,
    get_current_auth,
    hash_password,
    request_ip_hash,
    require_csrf,
    user_to_response,
)
from .database import get_db
from .models import AuditRecord, AuthSession, User
from .rate_limit import check_rate_limit
from .security import (
    clear_auth_cookies,
    new_secret,
    secret_hash,
    session_expiry,
    set_auth_cookies,
    validate_double_submit_csrf,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def _issue_session(
    request: Request,
    response: Response,
    db: AsyncSession,
    user: User,
) -> None:
    session_token = new_secret()
    csrf_token = new_secret()
    auth_session = AuthSession(
        user_id=user.id,
        token_hash=secret_hash(session_token),
        csrf_hash=secret_hash(csrf_token),
        expires_at=session_expiry(),
        ip_hash=request_ip_hash(request),
        user_agent=request.headers.get("user-agent", "")[:300] or None,
    )
    db.add(auth_session)
    await db.commit()
    set_auth_cookies(response, session_token, csrf_token)


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(
    user_data: UserCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    validate_double_submit_csrf(request)
    await check_rate_limit(f"signup:{request_ip_hash(request)}", 5, 60 * 60)
    user = User(
        email=str(user_data.email).lower(),
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"field": "email", "message": "Email already registered"},
        )
    await _issue_session(request, response, db, user)
    return AuthResponse(user=user_to_response(user))


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    validate_double_submit_csrf(request)
    key = f"login:{request_ip_hash(request)}:{secret_hash(str(user_data.email))[:16]}"
    await check_rate_limit(key, 5, 15 * 60)
    user = await authenticate_user(db, str(user_data.email), user_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    await _issue_session(request, response, db, user)
    return AuthResponse(user=user_to_response(user))


@router.post("/logout")
async def logout(
    response: Response,
    current: CurrentAuth = Depends(require_csrf),
    db: AsyncSession = Depends(get_db),
):
    current.auth_session.revoked_at = datetime.now(timezone.utc)
    db.add(
        AuditRecord(
            user_id=current.user.id,
            event_type="logout",
            details={"session_id": current.auth_session.id},
        )
    )
    await db.commit()
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current: CurrentAuth = Depends(require_csrf),
    db: AsyncSession = Depends(get_db),
):
    if not authenticate_password(current.user, payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "current_password", "message": "Password is incorrect"},
        )
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "new_password", "message": "Choose a new password"},
        )
    current.user.password_hash = hash_password(payload.new_password)
    current.user.must_change_password = False
    await db.execute(
        update(AuthSession)
        .where(
            AuthSession.user_id == current.user.id,
            AuthSession.id != current.auth_session.id,
            AuthSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    db.add(
        AuditRecord(
            user_id=current.user.id,
            event_type="password_changed",
            details={},
        )
    )
    await db.commit()
    return user_to_response(current.user)


def authenticate_password(user: User, password: str) -> bool:
    from .auth import verify_password

    return verify_password(password, user.password_hash)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current: CurrentAuth = Depends(get_current_auth),
):
    return user_to_response(current.user)
