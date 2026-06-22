import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .auth_routes import router as auth_router
from .config import get_settings
from .database import AsyncSessionFactory, close_database, create_dev_schema
from .rate_limit import close_redis, get_redis
from .security import set_public_csrf_cookie
from .session_routes import router as session_router

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(message)s",
)
logger = logging.getLogger("companion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    try:
        await create_dev_schema()
        if settings.is_production:
            if not settings.allowed_origins or "*" in settings.allowed_origins:
                raise RuntimeError("Production CORS origins must be explicit")
            async with AsyncSessionFactory() as db:
                await db.execute(text("SELECT 1"))
            await get_redis()
        yield
    finally:
        await close_redis()
        await close_database()


app = FastAPI(
    title="Mental Health KRR System",
    version="3.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "HEAD"],
    allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID"],
)


@app.middleware("http")
async def observability_and_security(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            json.dumps(
                {
                    "event": "request_failed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                }
            )
        )
        raise
    duration_ms = int((time.perf_counter() - started) * 1000)
    response.headers["X-Request-ID"] = request_id
    if getattr(request.state, "auth_session", None):
        session_token = request.cookies.get(settings.session_cookie_name)
        csrf_token = request.cookies.get(settings.csrf_cookie_name)
        if session_token and csrf_token:
            from .security import set_auth_cookies

            set_auth_cookies(response, session_token, csrf_token)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    logger.info(
        json.dumps(
            {
                "event": "request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    return response


app.include_router(auth_router, prefix="/api")
app.include_router(session_router, prefix="/api")


@app.get("/api/config/public")
async def public_config(request: Request, response: Response):
    if not request.cookies.get(settings.csrf_cookie_name):
        set_public_csrf_cookie(response)
    return {
        "support_email": settings.support_email,
        "provider_processing_enabled": (
            os.getenv("ENABLE_LLM", "false").lower() == "true"
        ),
        "deleted_conversation_retention_days": (
            settings.deleted_conversation_retention_days
        ),
        "security_log_retention_days": settings.security_log_retention_days,
        "region": "Pakistan",
    }


@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "active", "service": "Mental Health KRR System"}


@app.api_route("/api/ready", methods=["GET", "HEAD"])
async def readiness_check():
    checks = {"database": False, "redis": False}
    try:
        async with AsyncSessionFactory() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass
    try:
        redis = await get_redis()
        checks["redis"] = redis is not None or not settings.is_production
    except Exception:
        pass
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail={"checks": checks})
    return {"status": "ready", "checks": checks}


FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIR / "assets"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"

if FRONTEND_ASSETS_DIR.is_dir() and FRONTEND_INDEX.is_file():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_ASSETS_DIR)),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        del full_path
        return FileResponse(str(FRONTEND_INDEX))
else:
    logger.warning("Frontend build not found; API-only mode is active.")

    @app.get("/")
    async def api_root():
        return {
            "service": "Mental Health KRR System",
            "status": "api-only",
            "docs": "/docs",
        }
