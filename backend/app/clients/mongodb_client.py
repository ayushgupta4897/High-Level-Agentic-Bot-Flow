"""MongoDB client for database operations"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import motor.motor_asyncio

from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client wrapper"""
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes"""
        if self.database is None:
            return
        
        # Conversations collection indexes
        await self.database.conversations.create_index([
            ("session_id", 1), 
            ("timestamp", -1)
        ])
        
        # Preferences collection indexes
        await self.database.preferences.create_index([
            ("session_id", 1), 
            ("key", 1)
        ], unique=True)
        
        # Sessions collection indexes
        await self.database.sessions.create_index([
            ("session_id", 1)
        ], unique=True)
        await self.database.sessions.create_index([
            ("last_updated", -1)
        ])
        
        logger.info("Database indexes created")
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Save conversation message"""
        if self.database is None:
            raise Exception("Database not connected")
        
        message = {
            "session_id": session_id,
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        await self.database.conversations.insert_one(message)
        logger.debug(f"Saved message for session {session_id}")
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        if self.database is None:
            return []
        
        cursor = self.database.conversations.find(
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
    
    async def save_preference(
        self, 
        session_id: str, 
        key: str, 
        value: Any
    ):
        """Save user preference"""
        if self.database is None:
            raise Exception("Database not connected")
        
        await self.database.preferences.update_one(
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
        if self.database is None:
            return {}
        
        cursor = self.database.preferences.find({"session_id": session_id})
        
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
        if self.database is None:
            return None
        
        result = await self.database.preferences.find_one({
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
        if self.database is None:
            return
        
        await self.database.preferences.delete_one({
            "session_id": session_id,
            "key": key
        })
        logger.debug(f"Deleted preference {key} for session {session_id}")
    
    async def clear_session(self, session_id: str):
        """Clear all data for session"""
        if self.database is None:
            return
        
        # Delete conversations
        await self.database.conversations.delete_many({"session_id": session_id})
        
        # Delete preferences
        await self.database.preferences.delete_many({"session_id": session_id})
        
        # Delete session metadata
        await self.database.sessions.delete_one({"session_id": session_id})
        
        logger.info(f"Cleared session data: {session_id}")
    
    async def create_or_update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        last_message: Optional[str] = None
    ):
        """Create or update session metadata"""
        if self.database is None:
            return
        
        # Generate title if not provided
        if not title and last_message:
            title = await self._generate_session_title(session_id, last_message)
        
        if not title:
            title = f"Chat Session {session_id[:8]}"
        
        await self.database.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "title": title,
                    "last_updated": datetime.utcnow(),
                    "last_message": last_message
                },
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.debug(f"Updated session metadata: {session_id}")
    
    async def _generate_session_title(self, session_id: str, latest_message: str) -> str:
        """Generate intelligent session title based on conversation content"""
        # Get conversation history to understand context
        messages = await self.get_conversation_history(session_id, limit=5)
        preferences = await self.get_preferences(session_id)
        
        # Extract key information for title
        destination = preferences.get("destination")
        origin = preferences.get("origin")
        budget = preferences.get("budget")
        
        # Title generation logic
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
            words = latest_message.lower().split()
            travel_keywords = ['trip', 'travel', 'vacation', 'holiday', 'visit', 'tour']
            
            if any(keyword in words for keyword in travel_keywords):
                return "Travel Planning"
            else:
                return f"Chat {datetime.utcnow().strftime('%b %d')}"
    
    async def get_all_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all sessions with metadata"""
        if self.database is None:
            return []
        
        # Get sessions ordered by last_updated
        sessions_cursor = self.database.sessions.find().sort("last_updated", -1).limit(limit)
        
        sessions = []
        async for session in sessions_cursor:
            session_id = session["session_id"]
            
            # Get message count
            message_count = await self.database.conversations.count_documents(
                {"session_id": session_id}
            )
            
            # Get preferences for destination and budget
            preferences = await self.get_preferences(session_id)
            
            sessions.append({
                "session_id": session_id,
                "title": session.get("title", f"Chat {session_id[:8]}"),
                "last_message": session.get("last_message"),
                "last_updated": session.get("last_updated", session.get("created_at")),
                "created_at": session.get("created_at"),
                "message_count": message_count,
                "destination": preferences.get("destination"),
                "budget": preferences.get("budget")
            })
        
        return sessions
    
    async def update_session_title(self, session_id: str, title: str):
        """Update session title"""
        if self.database is None:
            return
        
        await self.database.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "title": title,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        logger.debug(f"Updated session title: {session_id} -> {title}")

# Global client instance
mongodb_client = MongoDBClient()
