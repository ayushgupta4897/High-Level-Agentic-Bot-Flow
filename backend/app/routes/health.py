"""Health check API routes"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.core.schemas import HealthResponse, DatabaseHealthResponse
from app.clients.mongodb_client import mongodb_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    
    return HealthResponse(
        status="healthy",
        service="Travel Agent API",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@router.get("/database", response_model=DatabaseHealthResponse)
async def database_health():
    """Database health check"""
    
    try:
        # Test MongoDB connection
        if mongodb_client.database is None:
            await mongodb_client.connect()
        
        # Ping database
        await mongodb_client.client.admin.command('ping')
        
        return DatabaseHealthResponse(
            status="healthy",
            database="connected",
            type="MongoDB"
        )
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return DatabaseHealthResponse(
            status="unhealthy",
            database="disconnected",
            type="MongoDB"
        )

@router.get("/ready")
async def readiness_check():
    """Readiness check for deployment"""
    
    try:
        # Check database connection
        if mongodb_client.database is None:
            await mongodb_client.connect()
        
        await mongodb_client.client.admin.command('ping')
        
        return {
            "status": "ready",
            "checks": {
                "database": "connected",
                "openai": "configured"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )
