from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import get_db
from .models import AuthSession, User
from .security import (
    hash_identifier,
    safe_equal_hash,
    secret_hash,
    session_expiry,
    validate_double_submit_csrf,
)

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)


class UserResponse(BaseModel):
    user_id: str
    email: str
    created_at: str
    must_change_password: bool


class AuthResponse(BaseModel):
    user: UserResponse


@dataclass
class CurrentAuth:
    user: User
    auth_session: AuthSession


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email.strip().lower()))


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


async def get_current_auth(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CurrentAuth:
    token = request.cookies.get(settings.session_cookie_name)
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )
    if not token:
        raise unauthorized

    auth_session = await db.scalar(
        select(AuthSession).where(AuthSession.token_hash == secret_hash(token))
    )
    now = datetime.now(timezone.utc)
    if (
        auth_session is None
        or auth_session.revoked_at is not None
        or _as_utc(auth_session.expires_at) <= now
    ):
        raise unauthorized

    user = await db.get(User, auth_session.user_id)
    if user is None:
        raise unauthorized

    auth_session.last_seen_at = now
    auth_session.expires_at = session_expiry()
    await db.commit()
    request.state.auth_session = auth_session
    request.state.user = user
    return CurrentAuth(user=user, auth_session=auth_session)


async def get_current_user(
    current: CurrentAuth = Depends(get_current_auth),
) -> User:
    return current.user


async def require_csrf(
    request: Request,
    current: CurrentAuth = Depends(get_current_auth),
) -> CurrentAuth:
    token = validate_double_submit_csrf(request)
    if not safe_equal_hash(token, current.auth_session.csrf_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )
    return current


def request_ip_hash(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",", 1)[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    return hash_identifier(ip)


def user_to_response(user: User) -> UserResponse:
    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return UserResponse(
        user_id=user.id,
        email=user.email,
        created_at=created_at.isoformat().replace("+00:00", "Z"),
        must_change_password=user.must_change_password,
    )
