"""Repository for conversation data access"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Repository for conversation data operations"""
    
    def __init__(self):
        self.db_client = mongodb_client
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save conversation message"""
        if self.db_client.database is None:
            raise Exception("Database not connected")
        
        message = {
            "session_id": session_id,
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        await self.db_client.database.conversations.insert_one(message)
        logger.debug(f"Saved message for session {session_id}")
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        if self.db_client.database is None:
            return []
        
        cursor = self.db_client.database.conversations.find(
            {"session_id": session_id}
        ).sort("timestamp", -1).limit(limit)
        
        messages = []
        async for message in cursor:
            messages.append({
                "role": message["role"],
                "content": message["content"],
                "timestamp": message["timestamp"].isoformat() if message.get("timestamp") else None,
                "metadata": message.get("metadata", {})
            })
        
        return list(reversed(messages))  # Return in chronological order
    
    async def get_message_count(self, session_id: str) -> int:
        """Get message count for session"""
        if self.db_client.database is None:
            return 0
        
        return await self.db_client.database.conversations.count_documents(
            {"session_id": session_id}
        )
    
    async def delete_conversation(self, session_id: str):
        """Delete all messages for session"""
        if self.db_client.database is None:
            return
        
        await self.db_client.database.conversations.delete_many({"session_id": session_id})
        logger.info(f"Deleted conversation for session: {session_id}")


# Global repository instance
conversation_repository = ConversationRepository()
