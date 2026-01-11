"""
Session persistence module for the Mental Health Companion application.
Handles session storage, retrieval, and management in JSON files.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import uuid
import re

from pydantic import BaseModel, Field


# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
SESSIONS_DIR = DATA_DIR / "sessions"


# ============================================================================
# Models
# ============================================================================

class SessionMessage(BaseModel):
    """A single message in a session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metadata: Optional[Dict[str, Any]] = None


class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    title: Optional[str] = None


class SessionSummary(BaseModel):
    """Summary view of a session for listing"""
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    risk_level: str = "low"
    last_message_preview: Optional[str] = None


class Session(BaseModel):
    """Full session model with all messages"""
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[SessionMessage] = []
    inferred_states: List[str] = []
    risk_level: str = "low"
    is_deleted: bool = False


class MessageRequest(BaseModel):
    """Request to send a message"""
    text: str


# ============================================================================
# Session Storage Functions
# ============================================================================

def _get_user_sessions_dir(user_id: str) -> Path:
    """Get the sessions directory for a specific user"""
    user_dir = SESSIONS_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _get_session_file(user_id: str, session_id: str) -> Path:
    """Get the file path for a specific session"""
    return _get_user_sessions_dir(user_id) / f"{session_id}.json"


def _generate_title_from_message(message: str) -> str:
    """
    Generate a session title from the first user message.
    Cleans and truncates the message to create a readable title.
    """
    # Remove extra whitespace
    clean = " ".join(message.split())
    
    # Truncate to reasonable length
    if len(clean) > 50:
        # Try to truncate at a word boundary
        truncated = clean[:47]
        last_space = truncated.rfind(" ")
        if last_space > 30:
            truncated = truncated[:last_space]
        return truncated + "..."
    
    return clean if clean else "New Conversation"


def create_session(user_id: str, title: Optional[str] = None) -> Session:
    """Create a new session for a user"""
    session = Session(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        title=title or "New Conversation",
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z",
        messages=[],
        inferred_states=[],
        risk_level="low"
    )
    
    # Save to file
    session_file = _get_session_file(user_id, session.session_id)
    session_file.write_text(json.dumps(session.model_dump(), indent=2))
    
    return session


def get_session(user_id: str, session_id: str) -> Optional[Session]:
    """Get a session by ID, ensuring it belongs to the user"""
    session_file = _get_session_file(user_id, session_id)
    
    if not session_file.exists():
        return None
    
    try:
        data = json.loads(session_file.read_text())
        session = Session(**data)
        
        # Verify ownership
        if session.user_id != user_id:
            return None
        
        # Don't return deleted sessions
        if session.is_deleted:
            return None
            
        return session
    except (json.JSONDecodeError, Exception):
        return None


def update_session(session: Session) -> Session:
    """Update a session in storage"""
    session.updated_at = datetime.utcnow().isoformat() + "Z"
    session_file = _get_session_file(session.user_id, session.session_id)
    session_file.write_text(json.dumps(session.model_dump(), indent=2))
    return session


def list_sessions(user_id: str) -> List[SessionSummary]:
    """List all sessions for a user (excluding deleted)"""
    user_dir = _get_user_sessions_dir(user_id)
    sessions = []
    
    for session_file in user_dir.glob("*.json"):
        try:
            data = json.loads(session_file.read_text())
            session = Session(**data)
            
            # Skip deleted sessions
            if session.is_deleted:
                continue
            
            # Get last message preview
            last_preview = None
            if session.messages:
                last_msg = session.messages[-1]
                preview = last_msg.content[:100]
                if len(last_msg.content) > 100:
                    preview += "..."
                last_preview = preview
            
            summary = SessionSummary(
                session_id=session.session_id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=len(session.messages),
                risk_level=session.risk_level,
                last_message_preview=last_preview
            )
            sessions.append(summary)
        except (json.JSONDecodeError, Exception):
            continue
    
    # Sort by updated_at descending (most recent first)
    sessions.sort(key=lambda s: s.updated_at, reverse=True)
    
    return sessions


def delete_session(user_id: str, session_id: str) -> bool:
    """Soft delete a session"""
    session = get_session(user_id, session_id)
    if not session:
        return False
    
    session.is_deleted = True
    update_session(session)
    return True


def add_message_to_session(
    session: Session,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> SessionMessage:
    """Add a message to a session"""
    message = SessionMessage(
        role=role,
        content=content,
        metadata=metadata
    )
    
    session.messages.append(message)
    
    # Auto-generate title from first user message
    if len(session.messages) == 1 and role == "user" and session.title == "New Conversation":
        session.title = _generate_title_from_message(content)
    
    update_session(session)
    return message


def update_session_risk(session: Session, risk_level: str):
    """Update the risk level of a session"""
    if risk_level in ["low", "medium", "high"]:
        session.risk_level = risk_level
        update_session(session)


def add_inferred_state(session: Session, state: str):
    """Add an inferred state to the session if not already present"""
    if state and state not in session.inferred_states:
        session.inferred_states.append(state)
        update_session(session)
