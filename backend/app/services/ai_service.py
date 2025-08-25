"""Service for AI operations and business logic"""

import json
import logging
from typing import Dict, List, Any, Optional

from app.clients.openai_client import openai_client
from app.config.prompts import (
    INTENT_ANALYSIS_SYSTEM, INTENT_ANALYSIS_USER,
    RESPONSE_GENERATION_SYSTEM, TRAVEL_RESPONSE_PROMPT,
    MEMORY_EXTRACTION_SYSTEM, MEMORY_EXTRACTION_USER
)

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI operations and business logic"""
    
    def __init__(self):
        self.ai_client = openai_client
    
    async def analyze_message_intent(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user message intent and extract entities"""
        
        messages = [
            {"role": "system", "content": INTENT_ANALYSIS_SYSTEM},
            {"role": "user", "content": INTENT_ANALYSIS_USER.format(
                context=json.dumps(context), 
                message=message
            )}
        ]
        
        try:
            response = await self.ai_client.chat_completion(
                messages, 
                temperature=0.3, 
                response_format="json"
            )
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent analysis JSON: {response}")
            return {
                "intent": "general",
                "entities": {},
                "requires_clarification": True,
                "confidence": "low"
            }
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            raise Exception(f"Intent analysis failed: {str(e)}")
    
    async def extract_user_preferences(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract user preferences from conversation"""
        
        # Get current preferences from context
        current_preferences = context.get("preferences", {})
        
        messages = [
            {"role": "system", "content": MEMORY_EXTRACTION_SYSTEM},
            {"role": "user", "content": MEMORY_EXTRACTION_USER.format(
                message=message,
                context=json.dumps(context),
                current_preferences=json.dumps(current_preferences)
            )}
        ]
        
        try:
            response = await self.ai_client.chat_completion(
                messages, 
                temperature=0.1, 
                response_format="json"
            )
            preferences = json.loads(response)
            
            # Filter out null values to avoid overwriting existing preferences with null
            filtered_preferences = {k: v for k, v in preferences.items() if v is not None}
            
            return filtered_preferences
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse preferences JSON: {response}")
            return {}
        except Exception as e:
            logger.error(f"Preference extraction failed: {str(e)}")
            return {}
    
    async def generate_travel_response(
        self, 
        user_message: str, 
        context: Dict[str, Any], 
        search_results: Optional[str] = None
    ) -> str:
        """Generate conversational response for travel queries"""
        
        messages = [
            {"role": "system", "content": RESPONSE_GENERATION_SYSTEM},
            {"role": "user", "content": TRAVEL_RESPONSE_PROMPT.format(
                user_message=user_message,
                context=json.dumps(context),
                search_results=search_results or "No search results available"
            )}
        ]
        
        try:
            return await self.ai_client.chat_completion(messages, temperature=0.8)
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise Exception(f"Response generation failed: {str(e)}")
    
    async def generate_travel_response_stream(
        self, 
        user_message: str, 
        context: Dict[str, Any], 
        search_results: Optional[str] = None
    ):
        """Generate streaming conversational response for travel queries"""
        
        messages = [
            {"role": "system", "content": RESPONSE_GENERATION_SYSTEM},
            {"role": "user", "content": TRAVEL_RESPONSE_PROMPT.format(
                user_message=user_message,
                context=json.dumps(context),
                search_results=search_results or "No search results available"
            )}
        ]
        
        try:
            async for chunk in self.ai_client.chat_completion_stream(messages, temperature=0.8):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming response generation failed: {str(e)}")
            raise Exception(f"Streaming response generation failed: {str(e)}")
    
    async def perform_web_search(self, query: str) -> str:
        """Perform web search for travel information"""
        try:
            return await self.ai_client.web_search(query)
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            raise Exception(f"Web search failed: {str(e)}")


# Global service instance
ai_service = AIService()
