"""Repository for user preference data access"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)


class PreferenceRepository:
    """Repository for user preference data operations"""
    
    def __init__(self):
        self.db_client = mongodb_client
    
    async def save_preference(
        self, 
        session_id: str, 
        key: str, 
        value: Any
    ):
        """Save user preference"""
        if self.db_client.database is None:
            raise Exception("Database not connected")
        
        await self.db_client.database.preferences.update_one(
            {"session_id": session_id, "key": key},
            {
                "$set": {
                    "value": value,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "session_id": session_id,
                    "key": key,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.debug(f"Saved preference {key} for session {session_id}")
    
    async def get_preferences(
        self, 
        session_id: str
    ) -> Dict[str, Any]:
        """Get all preferences for session"""
        if self.db_client.database is None:
            return {}
        
        cursor = self.db_client.database.preferences.find({"session_id": session_id})
        
        preferences = {}
        async for pref in cursor:
            preferences[pref["key"]] = pref["value"]
        
        return preferences
    
    async def get_preference(
        self, 
        session_id: str, 
        key: str
    ) -> Optional[Any]:
        """Get specific preference"""
        if self.db_client.database is None:
            return None
        
        result = await self.db_client.database.preferences.find_one({
            "session_id": session_id,
            "key": key
        })
        
        return result["value"] if result else None
    
    async def delete_preference(
        self, 
        session_id: str, 
        key: str
    ):
        """Delete specific preference"""
        if self.db_client.database is None:
            return
        
        await self.db_client.database.preferences.delete_one({
            "session_id": session_id,
            "key": key
        })
        logger.debug(f"Deleted preference {key} for session {session_id}")
    
    async def delete_all_preferences(self, session_id: str):
        """Delete all preferences for session"""
        if self.db_client.database is None:
            return
        
        await self.db_client.database.preferences.delete_many({"session_id": session_id})
        logger.info(f"Deleted all preferences for session: {session_id}")


# Global repository instance
preference_repository = PreferenceRepository()
