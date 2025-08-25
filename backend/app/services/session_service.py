"""Service for session management business logic"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.repositories.session_repository import session_repository
from app.repositories.conversation_repository import conversation_repository
from app.repositories.preference_repository import preference_repository

logger = logging.getLogger(__name__)


class SessionService:
    """Service for session management business operations"""
    
    def __init__(self):
        self.session_repo = session_repository
        self.conversation_repo = conversation_repository
        self.preference_repo = preference_repository
    
    def _generate_session_title(
        self, 
        preferences: Dict[str, Any], 
        latest_message: Optional[str] = None
    ) -> str:
        """Generate intelligent session title based on conversation content"""
        
        # Extract key information for title
        destination = preferences.get("destination")
        origin = preferences.get("origin")
        budget = preferences.get("budget")
        
        # Title generation logic based on travel preferences
        if destination and origin:
            if budget:
                return f"{origin} to {destination} Trip (₹{budget:,})"
            else:
                return f"{origin} to {destination} Trip"
        elif destination:
            if budget:
                return f"{destination} Trip (₹{budget:,})"
            else:
                return f"{destination} Travel Plan"
        else:
            # Extract key words from latest message
            if latest_message:
                words = latest_message.lower().split()
                travel_keywords = ['trip', 'travel', 'vacation', 'holiday', 'visit', 'tour']
                
                if any(keyword in words for keyword in travel_keywords):
                    return "Travel Planning"
            
            # Default fallback
            return f"Chat {datetime.utcnow().strftime('%b %d')}"
    
    async def create_or_update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        last_message: Optional[str] = None
    ):
        """Create or update session with intelligent title generation"""
        
        # If no title provided and we have a message, generate intelligent title
        if not title and last_message:
            preferences = await self.preference_repo.get_preferences(session_id)
            title = self._generate_session_title(preferences, last_message)
        
        if not title:
            title = f"Chat Session {session_id[:8]}"
        
        await self.session_repo.upsert_session(session_id, title, last_message)
        logger.debug(f"Updated session: {session_id} with title: {title}")
    
    async def update_session_title(self, session_id: str, title: str):
        """Update session title"""
        await self.session_repo.update_session(session_id, title=title)
        logger.debug(f"Updated session title: {session_id} -> {title}")
    
    async def get_all_sessions_with_metadata(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all sessions with complete metadata including message counts and preferences"""
        sessions = await self.session_repo.get_all_sessions(limit)
        
        # Enrich each session with additional metadata
        enriched_sessions = []
        for session in sessions:
            session_id = session["session_id"]
            
            # Get message count
            message_count = await self.conversation_repo.get_message_count(session_id)
            
            # Get preferences for destination and budget
            preferences = await self.preference_repo.get_preferences(session_id)
            
            # Build enriched session data
            enriched_session = {
                "session_id": session_id,
                "title": session.get("title", f"Chat {session_id[:8]}"),
                "last_message": session.get("last_message"),
                "last_updated": session.get("last_updated", session.get("created_at")),
                "created_at": session.get("created_at"),
                "message_count": message_count,
                "destination": preferences.get("destination"),
                "budget": preferences.get("budget")
            }
            
            enriched_sessions.append(enriched_session)
        
        return enriched_sessions
    
    async def delete_session_completely(self, session_id: str):
        """Delete session and all associated data"""
        # Delete conversation history
        await self.conversation_repo.delete_conversation(session_id)
        
        # Delete preferences
        await self.preference_repo.delete_all_preferences(session_id)
        
        # Delete session metadata
        await self.session_repo.delete_session(session_id)
        
        logger.info(f"Completely deleted session: {session_id}")
    
    async def regenerate_session_title(self, session_id: str):
        """Regenerate session title based on current preferences and recent messages"""
        # Get recent messages and preferences
        history = await self.conversation_repo.get_conversation_history(session_id, limit=1)
        preferences = await self.preference_repo.get_preferences(session_id)
        
        # Get the latest user message
        last_message = None
        if history:
            last_message = history[-1]["content"] if history[-1]["role"] == "user" else None
        
        # Generate new title
        new_title = self._generate_session_title(preferences, last_message)
        
        # Update session
        await self.session_repo.update_session(session_id, title=new_title)
        logger.debug(f"Regenerated title for session {session_id}: {new_title}")
        
        return new_title


# Global service instance
session_service = SessionService()
