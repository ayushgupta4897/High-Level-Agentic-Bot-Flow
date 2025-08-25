"""Service for conversation business logic"""

import logging
from typing import Dict, List, Any, Optional

from app.repositories.conversation_repository import conversation_repository
from app.repositories.preference_repository import preference_repository

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation business operations"""
    
    def __init__(self):
        self.conversation_repo = conversation_repository
        self.preference_repo = preference_repository
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save conversation message"""
        await self.conversation_repo.save_message(session_id, role, content, metadata)
        logger.debug(f"Saved {role} message for session {session_id}")
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        return await self.conversation_repo.get_conversation_history(session_id, limit)
    
    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get complete conversation context including history and preferences"""
        # Get conversation history
        history = await self.conversation_repo.get_conversation_history(session_id, limit=10)
        
        # Get user preferences
        preferences = await self.preference_repo.get_preferences(session_id)
        
        # Get message count
        message_count = await self.conversation_repo.get_message_count(session_id)
        
        return {
            "session_id": session_id,
            "history": history,
            "preferences": preferences,
            "message_count": message_count
        }
    
    async def clear_conversation(self, session_id: str):
        """Clear conversation history for session"""
        await self.conversation_repo.delete_conversation(session_id)
        logger.info(f"Cleared conversation for session: {session_id}")


# Global service instance
conversation_service = ConversationService()
