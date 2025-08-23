"""Unified memory management for conversations and preferences"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)

class MemoryManager:
    """Unified memory management system"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
    
    async def save_message(
        self, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save conversation message"""
        await mongodb_client.save_message(
            self.session_id, 
            role, 
            content, 
            metadata
        )
        logger.debug(f"Saved {role} message for session {self.session_id}")
    
    async def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent conversation messages"""
        return await mongodb_client.get_conversation_history(self.session_id, limit)
    
    async def update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple user preferences"""
        updates = {}
        
        for key, value in preferences.items():
            if value is not None:  # Only update non-null values
                await mongodb_client.save_preference(self.session_id, key, value)
                updates[key] = value
                logger.debug(f"Updated preference {key} for session {self.session_id}")
        
        return updates
    
    async def get_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        return await mongodb_client.get_preferences(self.session_id)
    
    async def get_preference(self, key: str) -> Optional[Any]:
        """Get specific preference"""
        return await mongodb_client.get_preference(self.session_id, key)
    
    async def delete_preference(self, key: str):
        """Delete specific preference"""
        await mongodb_client.delete_preference(self.session_id, key)
    
    async def get_context(self) -> Dict[str, Any]:
        """Get complete context for the session"""
        # Get recent conversation
        messages = await self.get_conversation_history(limit=10)
        
        # Get current preferences
        preferences = await self.get_preferences()
        
        # Build context
        context = {
            "session_id": self.session_id,
            "conversation": {
                "messages": messages,
                "message_count": len(messages)
            },
            "preferences": preferences,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        return context
    
    async def get_travel_context(self) -> Dict[str, Any]:
        """Get travel-specific context"""
        preferences = await self.get_preferences()
        
        travel_context = {
            "destination": preferences.get("destination"),
            "origin": preferences.get("origin", "Delhi"),
            "budget": preferences.get("budget"),
            "dates": preferences.get("dates"),
            "people_count": preferences.get("people_count", 1),
            "dietary_preferences": preferences.get("dietary_preferences", []),
            "activity_preferences": preferences.get("activity_preferences", []),
            "accommodation_type": preferences.get("accommodation_type")
        }
        
        # Remove null values
        return {k: v for k, v in travel_context.items() if v is not None}
    
    async def clear_session(self):
        """Clear all session data"""
        await mongodb_client.clear_session(self.session_id)
        logger.info(f"Cleared all data for session {self.session_id}")
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        messages = await self.get_conversation_history(limit=50)
        preferences = await self.get_preferences()
        
        user_messages = [m for m in messages if m["role"] == "user"]
        
        summary = {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "preferences_count": len(preferences),
            "has_destination": bool(preferences.get("destination")),
            "has_budget": bool(preferences.get("budget")),
            "has_dates": bool(preferences.get("dates")),
            "last_user_message": user_messages[-1]["content"] if user_messages else None,
            "session_start": messages[0]["timestamp"] if messages else None
        }
        
        return summary
