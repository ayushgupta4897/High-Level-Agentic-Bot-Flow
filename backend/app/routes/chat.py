"""Chat API routes with SSE support"""

import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse

from app.core.schemas import (
    ChatMessageRequest, 
    ChatMessageResponse, 
    ConversationHistoryResponse,
    ContextResponse,
    ErrorResponse
)
from app.core.agent import TravelAgent
from app.core.sse import sse_generator
from app.core.memory import MemoryManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest, stream_response: str = "false"):
    """Send chat message with optional streaming support"""
    
    try:
        should_stream = stream_response.lower() == "true"
        
        if should_stream:
            # Return SSE streaming response
            from app.core.agent import TravelAgent
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
        else:
            # Regular non-streaming response
            agent = TravelAgent(request.session_id)
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
        from app.core.agent import TravelAgent
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
