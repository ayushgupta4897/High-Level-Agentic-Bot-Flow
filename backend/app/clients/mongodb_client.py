"""MongoDB client for basic database operations"""

import logging
from typing import Optional
import motor.motor_asyncio

from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client wrapper - handles connection and basic operations only"""
    
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
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            if self.client is None:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Global client instance
mongodb_client = MongoDBClient()
