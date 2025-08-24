"""Pydantic schemas for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessageRequest(BaseModel):
    """Chat message request schema"""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User message")

class ChatMessageResponse(BaseModel):
    """Chat message response schema"""
    response: str = Field(..., description="Agent response")
    timestamp: str = Field(..., description="Response timestamp")
    intent: str = Field(..., description="Detected intent")

class AgentAction(BaseModel):
    """Agent action schema for SSE events"""
    action_type: str = Field(..., description="Type of action")
    description: str = Field(..., description="Action description")
    timestamp: str = Field(..., description="Action timestamp")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional action data")

class MemoryUpdate(BaseModel):
    """Memory update schema for SSE events"""
    updates: Dict[str, Any] = Field(..., description="Updated preferences")

class TravelPreferences(BaseModel):
    """Travel preferences schema"""
    destination: Optional[str] = Field(default=None, description="Travel destination")
    origin: Optional[str] = Field(default=None, description="Origin city")
    budget: Optional[int] = Field(default=None, ge=1000, description="Budget in INR")
    dates: Optional[str] = Field(default=None, description="Travel dates")
    people_count: Optional[int] = Field(default=1, ge=1, le=20, description="Number of travelers")
    dietary_preferences: Optional[List[str]] = Field(default=[], description="Dietary preferences")
    activity_preferences: Optional[List[str]] = Field(default=[], description="Activity preferences")
    accommodation_type: Optional[str] = Field(default=None, description="Accommodation type preference")

class PreferencesRequest(BaseModel):
    """Preferences update request"""
    preferences: TravelPreferences

class PreferencesResponse(BaseModel):
    """Preferences response"""
    status: str = Field(..., description="Update status")
    updates: Dict[str, Any] = Field(..., description="Applied updates")
    session_id: str = Field(..., description="Session identifier")

class ConversationMessage(BaseModel):
    """Conversation message schema"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Message metadata")

class ConversationHistoryResponse(BaseModel):
    """Conversation history response"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ConversationMessage] = Field(..., description="Conversation messages")
    summary: Dict[str, Any] = Field(..., description="Conversation summary")

class ContextResponse(BaseModel):
    """Context response schema"""
    session_id: str = Field(..., description="Session identifier")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    conversation: Dict[str, Any] = Field(..., description="Conversation summary")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Check timestamp")

class DatabaseHealthResponse(BaseModel):
    """Database health response"""
    status: str = Field(..., description="Database status")
    database: str = Field(..., description="Database connection status")
    type: str = Field(..., description="Database type")

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")

# SSE Event Schemas
class SSEEvent(BaseModel):
    """Base SSE event schema"""
    type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp")

class AgentActionEvent(SSEEvent):
    """Agent action SSE event"""
    action_type: str = Field(..., description="Action type")
    description: str = Field(..., description="Action description")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Action data")

class MemoryUpdateEvent(SSEEvent):
    """Memory update SSE event"""
    updates: Dict[str, Any] = Field(..., description="Memory updates")

class ResponseEvent(SSEEvent):
    """Response SSE event"""
    content: str = Field(..., description="Response content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Response metadata")

class ErrorEvent(SSEEvent):
    """Error SSE event"""
    message: str = Field(..., description="Error message")

class TypingEvent(SSEEvent):
    """Typing indicator SSE event"""
    typing: bool = Field(..., description="Typing status")

# Session Management Schemas
class SessionSummary(BaseModel):
    """Session summary schema"""
    session_id: str = Field(..., description="Session identifier")
    title: str = Field(..., description="Session title/name")
    last_message: Optional[str] = Field(default=None, description="Last user message")
    last_updated: datetime = Field(..., description="Last updated timestamp")
    created_at: datetime = Field(..., description="Session creation time")
    message_count: int = Field(default=0, description="Total message count")
    destination: Optional[str] = Field(default=None, description="Travel destination if any")
    budget: Optional[int] = Field(default=None, description="Budget if specified")
    
class SessionListResponse(BaseModel):
    """Session list response"""
    sessions: List[SessionSummary] = Field(..., description="List of sessions")
    total: int = Field(..., description="Total session count")

class SessionUpdateRequest(BaseModel):
    """Session update request"""
    title: Optional[str] = Field(default=None, description="New session title")
    
class PreferenceUpdateRequest(BaseModel):
    """Enhanced preference update request"""
    session_id: str = Field(..., description="Session identifier")
    updates: Dict[str, Any] = Field(..., description="Preference updates to apply")
