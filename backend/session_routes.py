"""
Session management API routes for the Mental Health Companion application.
All routes require authentication.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
import logging

from .auth import User, get_current_user
from .session_store import (
    Session,
    SessionSummary,
    SessionCreate,
    MessageRequest,
    create_session,
    get_session,
    list_sessions,
    delete_session,
    add_message_to_session,
    update_session_risk,
    add_inferred_state,
    get_user_stats
)





# Import the AI pipeline
try:
    from agents.pipeline import process_message
except ImportError:
    print("WARNING: AI pipeline not available")
    process_message = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/stats")
async def get_session_statistics(current_user: User = Depends(get_current_user)):
    """
    Get statistics for the current user's sessions.
    """
    return get_user_stats(current_user.user_id)


@router.get("", response_model=List[SessionSummary])
async def get_user_sessions(current_user: User = Depends(get_current_user)):
    """
    List all sessions for the current user.
    
    Returns sessions sorted by last update time (most recent first).
    """
    return list_sessions(current_user.user_id)


@router.post("", response_model=Session)
async def create_new_session(
    session_data: SessionCreate = None,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session for the current user.
    
    Optionally provide a title, otherwise it will be auto-generated.
    """
    title = session_data.title if session_data else None
    return create_session(current_user.user_id, title)


@router.get("/{session_id}", response_model=Session)
async def get_session_by_id(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific session with all messages.
    
    Only returns sessions owned by the current user.
    """
    session = get_session(current_user.user_id, session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    message: MessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a session and get AI response.
    
    This integrates with the AI pipeline to process the message
    and generate an appropriate response.
    """
    session = get_session(current_user.user_id, session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if not message.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    # Add user message to session
    user_msg = add_message_to_session(
        session=session,
        role="user",
        content=message.text
    )
    
    # Process through AI pipeline
    if process_message is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI pipeline not available"
        )
    
    try:
        # Run the AI pipeline
        result = process_message(
            session_id=session_id,
            message=message.text
        )
        
        # Add assistant response to session
        assistant_msg = add_message_to_session(
            session=session,
            role="assistant",
            content=result.get("response", ""),
            metadata={
                "state": result.get("state"),
                "confidence": result.get("confidence"),
                "action": result.get("action"),
                "evidence": result.get("evidence"),
                "follow_up_questions": result.get("follow_up_questions", []),
                "disclaimer": result.get("disclaimer")
            }
        )
        
        # Update session risk level based on pipeline output
        state = result.get("state", "")
        if state:
            # Update inferred states
            add_inferred_state(session, state)
            
            # Determine risk level from state
            high_risk_indicators = ["panic", "crisis", "severe", "suicidal", "self-harm"]
            medium_risk_indicators = ["persistent", "chronic", "moderate", "depressive"]
            
            state_lower = state.lower()
            if any(ind in state_lower for ind in high_risk_indicators):
                update_session_risk(session, "high")
            elif any(ind in state_lower for ind in medium_risk_indicators):
                update_session_risk(session, "medium")
        
        # Return the full pipeline result plus message IDs
        return {
            "user_message_id": user_msg.id,
            "assistant_message_id": assistant_msg.id,
            "session_id": result.get("session_id", session_id),
            "response": result.get("response", ""),
            "state": result.get("state"),
            "confidence": result.get("confidence"),
            "action": result.get("action"),
            "evidence": result.get("evidence"),
            "follow_up_questions": result.get("follow_up_questions", []),
            "disclaimer": result.get("disclaimer")
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.delete("/{session_id}")
async def delete_session_by_id(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a session.
    
    The session data is preserved but marked as deleted
    and will not appear in listings.
    """
    success = delete_session(current_user.user_id, session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session deleted successfully"}
