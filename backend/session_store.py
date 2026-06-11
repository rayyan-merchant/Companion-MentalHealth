from datetime import datetime, timezone
from typing import Any, Literal, cast

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Assessment, Conversation, Message


def isoformat(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


class SessionMessage(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str
    metadata: dict[str, Any] | None = None


class SessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class SessionSummary(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    risk_level: Literal["low", "medium", "high"] = "low"
    last_message_preview: str | None = None


class Session(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[SessionMessage] = Field(default_factory=list)
    inferred_states: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"


class MessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    client_message_id: str = Field(
        min_length=8,
        max_length=80,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )


def generate_title(message: str) -> str:
    clean = " ".join(message.split())
    if len(clean) <= 50:
        return clean or "New Conversation"
    truncated = clean[:47]
    boundary = truncated.rfind(" ")
    if boundary > 30:
        truncated = truncated[:boundary]
    return f"{truncated}..."


def message_to_schema(message: Message) -> SessionMessage:
    return SessionMessage(
        id=message.id,
        role=cast(Literal["user", "assistant", "system"], message.role),
        content=message.content,
        timestamp=isoformat(message.created_at),
        metadata=message.message_metadata,
    )


def conversation_to_schema(
    conversation: Conversation,
    messages: list[Message] | None = None,
) -> Session:
    loaded_messages = conversation.messages if messages is None else messages
    return Session(
        session_id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=isoformat(conversation.created_at),
        updated_at=isoformat(conversation.updated_at),
        messages=[message_to_schema(item) for item in loaded_messages],
        inferred_states=conversation.inferred_states or [],
        risk_level=cast(
            Literal["low", "medium", "high"], conversation.risk_level
        ),
    )


async def create_session(
    db: AsyncSession,
    user_id: str,
    title: str | None = None,
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=(title or "New Conversation").strip() or "New Conversation",
        messages=[],
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
) -> Conversation | None:
    statement = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == session_id,
            Conversation.user_id == user_id,
            Conversation.deleted_at.is_(None),
        )
    )
    return await db.scalar(statement)


async def list_sessions(
    db: AsyncSession,
    user_id: str,
) -> list[SessionSummary]:
    conversations = (
        await db.scalars(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
            .order_by(Conversation.updated_at.desc())
        )
    ).all()
    summaries: list[SessionSummary] = []
    for conversation in conversations:
        preview = None
        if conversation.messages:
            content = conversation.messages[-1].content
            preview = content[:100] + ("..." if len(content) > 100 else "")
        summaries.append(
            SessionSummary(
                session_id=conversation.id,
                user_id=conversation.user_id,
                title=conversation.title,
                created_at=isoformat(conversation.created_at),
                updated_at=isoformat(conversation.updated_at),
                message_count=len(conversation.messages),
                risk_level=cast(
                    Literal["low", "medium", "high"],
                    conversation.risk_level,
                ),
                last_message_preview=preview,
            )
        )
    return summaries


async def soft_delete_session(
    db: AsyncSession,
    user_id: str,
    session_id: str,
) -> bool:
    conversation = await get_session(db, user_id, session_id)
    if conversation is None:
        return False
    conversation.deleted_at = datetime.now(timezone.utc)
    conversation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def find_idempotent_exchange(
    conversation: Conversation,
    client_message_id: str,
) -> tuple[Message, Message | None] | None:
    for index, message in enumerate(conversation.messages):
        if (
            message.role == "user"
            and message.client_message_id == client_message_id
        ):
            assistant = next(
                (
                    candidate
                    for candidate in conversation.messages[index + 1 :]
                    if candidate.role == "assistant"
                    and (candidate.message_metadata or {}).get("reply_to")
                    == client_message_id
                ),
                None,
            )
            return message, assistant
    return None


async def add_user_message(
    db: AsyncSession,
    conversation: Conversation,
    content: str,
    client_message_id: str,
) -> Message:
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content=content,
        client_message_id=client_message_id,
    )
    db.add(message)
    if not conversation.messages and conversation.title == "New Conversation":
        conversation.title = generate_title(content)
    conversation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(message)
    conversation.messages.append(message)
    return message


async def add_assistant_message(
    db: AsyncSession,
    conversation: Conversation,
    content: str,
    metadata: dict[str, Any],
    assessment_data: dict[str, Any],
) -> Message:
    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=content,
        message_metadata=metadata,
    )
    db.add(message)
    await db.flush()
    db.add(
        Assessment(
            conversation_id=conversation.id,
            message_id=message.id,
            **assessment_data,
        )
    )
    state = metadata.get("state")
    states = list(conversation.inferred_states or [])
    if state and state not in states:
        states.append(state)
        conversation.inferred_states = states
    conversation.risk_level = risk_level_for_result(
        state or "", metadata.get("crisis_type")
    )
    conversation.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(message)
    conversation.messages.append(message)
    return message


def risk_level_for_result(state: str, crisis_type: str | None) -> str:
    if crisis_type:
        return "high"
    lowered = state.lower()
    if any(word in lowered for word in ("panic", "crisis", "severe", "suicid")):
        return "high"
    if any(word in lowered for word in ("persistent", "moderate", "depress")):
        return "medium"
    return "low"


async def get_user_stats(db: AsyncSession, user_id: str) -> dict[str, Any]:
    conversations = (
        await db.scalars(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
        )
    ).all()
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    theme_counts: dict[str, int] = {}
    total_messages = 0
    for conversation in conversations:
        risk_counts[conversation.risk_level] += 1
        total_messages += len(conversation.messages)
        for state in conversation.inferred_states or []:
            theme_counts[state] = theme_counts.get(state, 0) + 1
    ranked_themes = sorted(
        theme_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]
    top_symptoms = [
        {"name": name, "count": count}
        for name, count in ranked_themes
    ]
    return {
        "total_sessions": len(conversations),
        "risk_distribution": risk_counts,
        "top_symptoms": top_symptoms,
        "total_messages": total_messages,
    }


async def get_recent_chat_history(
    db: AsyncSession,
    user_id: str,
    limit: int = 30,
) -> str:
    messages = (
        await db.scalars(
            select(Message)
            .join(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
    ).all()
    messages = list(reversed(messages))
    return "\n".join(
        f"{'User' if item.role == 'user' else 'Companion'}: {item.content}"
        for item in messages
    )
