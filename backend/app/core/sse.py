"""Server-Sent Events implementation for real-time agent updates"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Set
from sse_starlette import EventSourceResponse

logger = logging.getLogger(__name__)

class SSEManager:
    """Manages Server-Sent Events connections and broadcasts"""
    
    def __init__(self):
        self.connections: Dict[str, Set[asyncio.Queue]] = {}
    
    def add_connection(self, session_id: str, queue: asyncio.Queue):
        """Add a new SSE connection for a session"""
        if session_id not in self.connections:
            self.connections[session_id] = set()
        
        self.connections[session_id].add(queue)
        logger.debug(f"Added SSE connection for session: {session_id}")
    
    def remove_connection(self, session_id: str, queue: asyncio.Queue):
        """Remove SSE connection"""
        if session_id in self.connections:
            self.connections[session_id].discard(queue)
            
            # Clean up empty session
            if not self.connections[session_id]:
                del self.connections[session_id]
        
        logger.debug(f"Removed SSE connection for session: {session_id}")
    
    async def send_event(
        self, 
        session_id: str, 
        event_type: str, 
        data: Dict[str, Any]
    ):
        """Send event to all connections for a session"""
        if session_id not in self.connections:
            return
        
        event_data = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        
        # Send to all connections for this session
        disconnected_queues = []
        
        for queue in self.connections[session_id]:
            try:
                await queue.put(event_data)
            except Exception as e:
                logger.error(f"Failed to send SSE event: {e}")
                disconnected_queues.append(queue)
        
        # Clean up disconnected queues
        for queue in disconnected_queues:
            self.remove_connection(session_id, queue)
    
    async def send_agent_action(
        self, 
        session_id: str, 
        action_type: str, 
        description: str, 
        data: Optional[Dict[str, Any]] = None
    ):
        """Send agent action event"""
        await self.send_event(session_id, "agent_action", {
            "action_type": action_type,
            "description": description,
            "data": data or {}
        })
    
    async def send_memory_update(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ):
        """Send memory update event"""
        await self.send_event(session_id, "memory_update", {
            "updates": updates
        })
    
    async def send_response(
        self, 
        session_id: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send agent response event"""
        await self.send_event(session_id, "response", {
            "content": content,
            "metadata": metadata or {}
        })
    
    async def send_error(
        self, 
        session_id: str, 
        error_message: str
    ):
        """Send error event"""
        await self.send_event(session_id, "error", {
            "message": error_message
        })
    
    async def send_typing(
        self, 
        session_id: str, 
        typing: bool
    ):
        """Send typing indicator event"""
        await self.send_event(session_id, "typing", {
            "typing": typing
        })

# Global SSE manager instance
sse_manager = SSEManager()

async def sse_generator(session_id: str):
    """SSE event generator for a session"""
    queue = asyncio.Queue()
    sse_manager.add_connection(session_id, queue)
    
    try:
        # Send initial connection confirmation
        yield json.dumps({'type': 'connected', 'session_id': session_id})
        
        while True:
            # Wait for events
            try:
                event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield json.dumps(event_data)
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                heartbeat_data = {
                    'type': 'heartbeat', 
                    'timestamp': datetime.utcnow().isoformat()
                }
                yield json.dumps(heartbeat_data)
    
    except (asyncio.CancelledError, GeneratorExit):
        # Client disconnected
        logger.debug(f"SSE connection closed for session: {session_id}")
    
    except Exception as e:
        logger.error(f"SSE generator error for session {session_id}: {e}")
    
    finally:
        # Clean up connection
        sse_manager.remove_connection(session_id, queue)
        logger.debug(f"Cleaned up SSE connection for session: {session_id}")
