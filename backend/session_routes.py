import asyncio
import logging
import time
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import CurrentAuth, get_current_auth, require_csrf
from .config import get_settings
from .database import AsyncSessionFactory, get_db
from .models import SafetyEvent
from .rate_limit import check_rate_limit, get_redis
from .session_store import (
    MessageRequest,
    Session,
    SessionCreate,
    SessionSummary,
    add_assistant_message,
    add_user_message,
    conversation_to_schema,
    create_session,
    find_idempotent_exchange,
    get_recent_chat_history,
    get_session,
    get_user_stats,
    list_sessions,
    soft_delete_session,
)

try:
    from agents.llm_explainer import generate_dashboard_insight
    from agents.pipeline import process_message
except ImportError:
    generate_dashboard_insight = None
    process_message = None


logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/sessions", tags=["Sessions"])
_insight_memory_cache: dict[str, tuple[float, str | None]] = {}


def _deterministic_insight(history: str) -> str:
    reflection_count = sum(
        1 for line in history.splitlines() if line.startswith("User:")
    )
    if reflection_count <= 1:
        return (
            "You have started making space to reflect. Consider naming one small "
            "thing that felt difficult and one support that may help today."
        )
    return (
        f"You have shared {reflection_count} recent reflections. Look for one "
        "repeating situation, feeling, or coping step that you may want to discuss "
        "with someone you trust."
    )


def _metadata_response(
    session_id: str,
    user_message_id: str,
    assistant_message_id: str,
    metadata: dict[str, Any],
    content: str,
) -> dict[str, Any]:
    return {
        "user_message_id": user_message_id,
        "assistant_message_id": assistant_message_id,
        "session_id": session_id,
        "response": content,
        "state": metadata.get("state"),
        "confidence": metadata.get("confidence"),
        "action": metadata.get("action"),
        "evidence": metadata.get("evidence", {}),
        "reasoning_trace": metadata.get("reasoning_trace", []),
        "follow_up_questions": metadata.get("follow_up_questions", []),
        "disclaimer": metadata.get("disclaimer", ""),
        "crisis_type": metadata.get("crisis_type"),
        "processing_ms": metadata.get("processing_ms", 0),
        "used_fallback": metadata.get("used_fallback", True),
        "rules_fired": metadata.get("rules_fired", []),
        "rule_version": metadata.get("rule_version", "unknown"),
    }


async def _get_cached_insight(user_id: str) -> str | None:
    redis = await get_redis()
    if redis is not None:
        value = await redis.get(f"insight:{user_id}")
        return value
    cached = _insight_memory_cache.get(user_id)
    if cached and cached[0] > time.time():
        return cached[1]
    return None


async def _generate_and_cache_insight(user_id: str) -> None:
    async with AsyncSessionFactory() as db:
        history = await get_recent_chat_history(db, user_id, limit=30)
    if not history:
        return
    insight = (
        await asyncio.to_thread(generate_dashboard_insight, history)
        if generate_dashboard_insight is not None
        else None
    )
    if not insight:
        insight = _deterministic_insight(history)
    redis = await get_redis()
    if redis is not None:
        await redis.setex(
            f"insight:{user_id}",
            settings.insight_cache_seconds,
            insight,
        )
    else:
        _insight_memory_cache[user_id] = (
            time.time() + settings.insight_cache_seconds,
            insight,
        )


@router.get("/stats")
async def get_session_statistics(
    current: CurrentAuth = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_stats(db, current.user.id)


@router.get("/insight")
async def get_dashboard_observation(
    background_tasks: BackgroundTasks,
    current: CurrentAuth = Depends(get_current_auth),
):
    await check_rate_limit(f"insight:{current.user.id}", 10, 60 * 60)
    cached = await _get_cached_insight(current.user.id)
    if cached is not None:
        return {"insight": cached, "status": "ready"}
    background_tasks.add_task(_generate_and_cache_insight, current.user.id)
    return {"insight": None, "status": "generating"}


@router.get("", response_model=list[SessionSummary])
async def get_user_sessions(
    q: str | None = Query(default=None, max_length=100),
    current: CurrentAuth = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    sessions = await list_sessions(db, current.user.id)
    if not q:
        return sessions
    query = q.strip().lower()
    return [
        item
        for item in sessions
        if query in item.title.lower()
        or query in (item.last_message_preview or "").lower()
    ]


@router.post("", response_model=Session, status_code=201)
async def create_new_session(
    session_data: SessionCreate | None = None,
    current: CurrentAuth = Depends(require_csrf),
    db: AsyncSession = Depends(get_db),
):
    conversation = await create_session(
        db,
        current.user.id,
        session_data.title if session_data else None,
    )
    return conversation_to_schema(conversation, messages=[])


@router.get("/{session_id}", response_model=Session)
async def get_session_by_id(
    session_id: str,
    current: CurrentAuth = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
):
    conversation = await get_session(db, current.user.id, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return conversation_to_schema(conversation)


@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    payload: MessageRequest,
    current: CurrentAuth = Depends(require_csrf),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(f"chat-minute:{current.user.id}", 20, 60)
    await check_rate_limit(f"chat-day:{current.user.id}", 200, 24 * 60 * 60)
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    conversation = await get_session(db, current.user.id, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")

    existing = await find_idempotent_exchange(
        conversation, payload.client_message_id
    )
    if existing and existing[1]:
        return _metadata_response(
            session_id,
            existing[0].id,
            existing[1].id,
            existing[1].message_metadata or {},
            existing[1].content,
        )
    user_message = (
        existing[0]
        if existing
        else await add_user_message(
            db,
            conversation,
            text,
            payload.client_message_id,
        )
    )
    if process_message is None:
        raise HTTPException(status_code=503, detail="Reasoning service unavailable")

    history = [
        {
            "id": item.id,
            "role": item.role,
            "content": item.content,
            "timestamp": item.created_at.isoformat(),
            "metadata": item.message_metadata,
        }
        for item in conversation.messages
        if item.id != user_message.id
    ]
    started = time.perf_counter()
    try:
        result = await asyncio.to_thread(
            process_message,
            session_id,
            text,
            history,
        )
    except Exception:
        request_id = getattr(current, "request_id", None)
        logger.exception(
            "pipeline_failed session=%s request_id=%s",
            session_id,
            request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Response generation timed out. Retry with the same message.",
        )
    processing_ms = int((time.perf_counter() - started) * 1000)
    rules_fired = result.get("rules_fired", [])
    reasoning_trace = [
        f"Applied rule {rule}" for rule in rules_fired
    ]
    metadata = {
        "reply_to": payload.client_message_id,
        "state": result.get("state"),
        "confidence": result.get("confidence"),
        "action": result.get("action"),
        "evidence": result.get("evidence", {}),
        "reasoning_trace": reasoning_trace,
        "follow_up_questions": result.get("follow_up_questions", []),
        "disclaimer": result.get("disclaimer", ""),
        "crisis_type": result.get("crisis_type"),
        "processing_ms": processing_ms,
        "used_fallback": result.get("used_fallback", True),
        "rules_fired": rules_fired,
        "rule_version": result.get("rule_version", "unknown"),
    }
    assistant = await add_assistant_message(
        db,
        conversation,
        result.get("response", ""),
        metadata,
        {
            "rule_version": metadata["rule_version"],
            "rules_fired": rules_fired,
            "evidence": metadata["evidence"],
            "confidence": result.get("confidence", "low"),
            "confidence_rationale": result.get("confidence_rationale", {}),
            "crisis_type": result.get("crisis_type"),
            "processing_ms": processing_ms,
            "used_fallback": result.get("used_fallback", True),
            "provider": result.get("provider"),
        },
    )
    if result.get("crisis_type"):
        db.add(
            SafetyEvent(
                user_id=current.user.id,
                conversation_id=conversation.id,
                event_type=result["crisis_type"],
                rule_version=metadata["rule_version"],
                redacted_context={
                    "rules_fired": rules_fired,
                    "evidence_categories": list(metadata["evidence"].keys()),
                },
            )
        )
        await db.commit()
    return _metadata_response(
        session_id,
        user_message.id,
        assistant.id,
        metadata,
        assistant.content,
    )


@router.delete("/{session_id}")
async def delete_session_by_id(
    session_id: str,
    current: CurrentAuth = Depends(require_csrf),
    db: AsyncSession = Depends(get_db),
):
    deleted = await soft_delete_session(db, current.user.id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}
