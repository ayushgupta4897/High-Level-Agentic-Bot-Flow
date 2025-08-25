"""Repository for session data access"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for session data operations"""
    
    def __init__(self):
        self.db_client = mongodb_client
    
    async def create_session(
        self,
        session_id: str,
        title: Optional[str] = None
    ):
        """Create new session metadata"""
        if self.db_client.database is None:
            return
        
        session_data = {
            "session_id": session_id,
            "title": title or f"Chat Session {session_id[:8]}",
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "last_message": None
        }
        
        await self.db_client.database.sessions.insert_one(session_data)
        logger.debug(f"Created session: {session_id}")
    
    async def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        last_message: Optional[str] = None
    ):
        """Update session metadata"""
        if self.db_client.database is None:
            return
        
        update_data = {"last_updated": datetime.utcnow()}
        
        if title:
            update_data["title"] = title
        if last_message:
            update_data["last_message"] = last_message
        
        await self.db_client.database.sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data},
            upsert=True
        )
        logger.debug(f"Updated session metadata: {session_id}")
    
    async def upsert_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        last_message: Optional[str] = None
    ):
        """Create or update session metadata"""
        if self.db_client.database is None:
            return
        
        update_data = {
            "last_updated": datetime.utcnow()
        }
        
        if title:
            update_data["title"] = title
        if last_message:
            update_data["last_message"] = last_message
        
        insert_data = {
            "session_id": session_id,
            "created_at": datetime.utcnow()
        }
        
        await self.db_client.database.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": update_data,
                "$setOnInsert": insert_data
            },
            upsert=True
        )
        logger.debug(f"Upserted session metadata: {session_id}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata"""
        if self.db_client.database is None:
            return None
        
        session = await self.db_client.database.sessions.find_one(
            {"session_id": session_id}
        )
        
        if session:
            # Remove MongoDB _id field
            session.pop('_id', None)
        
        return session
    
    async def get_all_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all sessions ordered by last_updated"""
        if self.db_client.database is None:
            return []
        
        cursor = self.db_client.database.sessions.find().sort("last_updated", -1).limit(limit)
        
        sessions = []
        async for session in cursor:
            # Remove MongoDB _id field
            session.pop('_id', None)
            sessions.append(session)
        
        return sessions
    
    async def delete_session(self, session_id: str):
        """Delete session metadata"""
        if self.db_client.database is None:
            return
        
        await self.db_client.database.sessions.delete_one({"session_id": session_id})
        logger.info(f"Deleted session metadata: {session_id}")


# Global repository instance
session_repository = SessionRepository()
