"""Chat API routes with comprehensive travel agent functionality"""

import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse

from app.core.schemas import (
    ChatMessageRequest, 
    ChatMessageResponse, 
    ConversationHistoryResponse,
    ContextResponse,
    ErrorResponse,
    SessionListResponse,
    SessionSummary,
    SessionUpdateRequest,
    PreferenceUpdateRequest
)
from app.core.agent import TravelAgent
from app.core.sse import sse_generator
from app.core.memory import MemoryManager
from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest, stream_response: str = "false"):
    """Send chat message with optional streaming support"""
    
    try:
        # Create agent instance at the start of the function
        agent = TravelAgent(request.session_id)
        should_stream = stream_response.lower() == "true"
        
        if should_stream:
            # Return SSE streaming response
            return EventSourceResponse(
                agent.process_message_stream(request.message),
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        else:
            # Regular non-streaming response
            result = await agent.process_message(request.message)
            
            return ChatMessageResponse(
                response=result["response"],
                timestamp=result["timestamp"],
                intent=result["intent"]
            )
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/message/stream")
async def send_message_stream(request: ChatMessageRequest):
    """Send chat message with streaming response (ChatGPT-like)"""
    
    try:
        agent = TravelAgent(request.session_id)
        
        return EventSourceResponse(
            agent.process_message_stream(request.message),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive", 
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stream message: {str(e)}"
        )

@router.get("/events/{session_id}")
async def get_events(session_id: str, request: Request):
    """Server-Sent Events endpoint for real-time agent updates"""
    
    try:
        return EventSourceResponse(
            sse_generator(session_id),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in SSE endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to establish event stream: {str(e)}"
        )

@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_id: str, limit: int = 20):
    """Get conversation history for a session"""
    
    try:
        memory = MemoryManager(session_id)
        messages = await memory.get_conversation_history(limit=limit)
        summary = await memory.get_summary()
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=messages,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation history: {str(e)}"
        )

@router.get("/context/{session_id}", response_model=ContextResponse)
async def get_context(session_id: str):
    """Get complete context for a session"""
    
    try:
        memory = MemoryManager(session_id)
        preferences = await memory.get_preferences()
        conversation = await memory.get_summary()
        
        return ContextResponse(
            session_id=session_id,
            preferences=preferences,
            conversation=conversation
        )
        
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context: {str(e)}"
        )

@router.get("/sessions", response_model=SessionListResponse)
async def get_all_sessions(limit: int = 50):
    """Get all chat sessions for the sidebar"""
    
    try:
        sessions_data = await mongodb_client.get_all_sessions(limit=limit)
        
        sessions = []
        for session_data in sessions_data:
            sessions.append(SessionSummary(
                session_id=session_data["session_id"],
                title=session_data["title"],
                last_message=session_data.get("last_message"),
                last_updated=session_data["last_updated"],
                created_at=session_data["created_at"],
                message_count=session_data["message_count"],
                destination=session_data.get("destination"),
                budget=session_data.get("budget")
            ))
        
        return SessionListResponse(
            sessions=sessions,
            total=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.put("/session/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
    """Update session title"""
    
    try:
        if request.title:
            await mongodb_client.update_session_title(session_id, request.title)
        
        return {
            "status": "success",
            "message": f"Session {session_id} updated",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session: {str(e)}"
        )

@router.post("/preferences")
async def update_preferences(request: PreferenceUpdateRequest):
    """Update user preferences for a session"""
    
    try:
        memory = MemoryManager(request.session_id)
        updates = await memory.update_preferences(request.updates)
        
        return {
            "status": "success",
            "message": "Preferences updated successfully",
            "session_id": request.session_id,
            "updates": updates
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear all data for a session"""
    
    try:
        memory = MemoryManager(session_id)
        await memory.clear_session()
        
        return {
            "status": "success",
            "message": f"Session {session_id} cleared",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )