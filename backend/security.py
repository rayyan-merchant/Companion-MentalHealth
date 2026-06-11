import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, Response, status

from .config import get_settings

settings = get_settings()


def new_secret() -> str:
    return secrets.token_urlsafe(32)


def secret_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_equal_hash(value: str, expected_hash: str) -> bool:
    return hmac.compare_digest(secret_hash(value), expected_hash)


def hash_identifier(value: str) -> str:
    return secret_hash(value)[:24]


def session_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.session_days)


def set_auth_cookies(
    response: Response,
    session_token: str,
    csrf_token: str,
) -> None:
    max_age = settings.session_days * 24 * 60 * 60
    response.set_cookie(
        settings.session_cookie_name,
        session_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
        max_age=max_age,
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        httponly=False,
        secure=settings.is_production,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
        max_age=max_age,
    )


def set_public_csrf_cookie(response: Response) -> str:
    token = new_secret()
    response.set_cookie(
        settings.csrf_cookie_name,
        token,
        httponly=False,
        secure=settings.is_production,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
        max_age=60 * 60,
    )
    return token


def clear_auth_cookies(response: Response) -> None:
    for name in (settings.session_cookie_name, settings.csrf_cookie_name):
        response.delete_cookie(
            name,
            domain=settings.cookie_domain,
            path="/",
            secure=settings.is_production,
            samesite="lax",
        )


def validate_double_submit_csrf(request: Request) -> str:
    cookie = request.cookies.get(settings.csrf_cookie_name)
    header = request.headers.get("X-CSRF-Token")
    if not cookie or not header or not hmac.compare_digest(cookie, header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )
    return header
