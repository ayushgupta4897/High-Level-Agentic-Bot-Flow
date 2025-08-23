"""OpenAI client for AI operations"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI

from app.config.settings import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI client wrapper for chat completions and web search"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Generate chat completion"""
        
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            if response_format == "json":
                params["response_format"] = {"type": "json_object"}
            
            if stream:
                # For streaming, we don't return here - this is handled by chat_completion_stream
                raise ValueError("Use chat_completion_stream for streaming responses")
            
            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {str(e)}")
            raise Exception(f"AI response failed: {str(e)}")
    
    async def chat_completion_stream(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """Generate streaming chat completion"""
        
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {str(e)}")
            raise Exception(f"AI streaming failed: {str(e)}")
    
    async def web_search(self, query: str) -> str:
        """Perform web search using OpenAI"""
        
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful assistant that can search the web for current information. Provide accurate, up-to-date information based on web search results."
            },
            {
                "role": "user",
                "content": f"Search the web for: {query}\n\nProvide comprehensive, current information about this topic."
            }
        ]
        
        try:
            # Note: This uses OpenAI's web search capability 
            # In practice, you'd integrate with a web search API or use OpenAI's browsing feature
            response = await self.chat_completion(messages, temperature=0.3)
            return response
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    async def analyze_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user message intent and extract entities"""
        
        from app.config.prompts import INTENT_ANALYSIS_SYSTEM, INTENT_ANALYSIS_USER
        
        messages = [
            {"role": "system", "content": INTENT_ANALYSIS_SYSTEM},
            {"role": "user", "content": INTENT_ANALYSIS_USER.format(
                context=json.dumps(context), 
                message=message
            )}
        ]
        
        try:
            response = await self.chat_completion(
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
    
    async def generate_response(
        self, 
        user_message: str, 
        context: Dict[str, Any], 
        search_results: Optional[str] = None
    ) -> str:
        """Generate conversational response"""
        
        from app.config.prompts import RESPONSE_GENERATION_SYSTEM, TRAVEL_RESPONSE_PROMPT
        
        messages = [
            {"role": "system", "content": RESPONSE_GENERATION_SYSTEM},
            {"role": "user", "content": TRAVEL_RESPONSE_PROMPT.format(
                user_message=user_message,
                context=json.dumps(context),
                search_results=search_results or "No search results available"
            )}
        ]
        
        return await self.chat_completion(messages, temperature=0.8)
    
    async def generate_response_stream(
        self, 
        user_message: str, 
        context: Dict[str, Any], 
        search_results: Optional[str] = None
    ):
        """Generate streaming conversational response"""
        
        from app.config.prompts import RESPONSE_GENERATION_SYSTEM, TRAVEL_RESPONSE_PROMPT
        
        messages = [
            {"role": "system", "content": RESPONSE_GENERATION_SYSTEM},
            {"role": "user", "content": TRAVEL_RESPONSE_PROMPT.format(
                user_message=user_message,
                context=json.dumps(context),
                search_results=search_results or "No search results available"
            )}
        ]
        
        async for chunk in self.chat_completion_stream(messages, temperature=0.8):
            yield chunk
    
    async def extract_preferences(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract user preferences from conversation"""
        
        from app.config.prompts import MEMORY_EXTRACTION_SYSTEM, MEMORY_EXTRACTION_USER
        
        messages = [
            {"role": "system", "content": MEMORY_EXTRACTION_SYSTEM},
            {"role": "user", "content": MEMORY_EXTRACTION_USER.format(
                message=message,
                context=json.dumps(context)
            )}
        ]
        
        try:
            response = await self.chat_completion(
                messages, 
                temperature=0.1, 
                response_format="json"
            )
            return json.loads(response)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse preferences JSON: {response}")
            return {}

# Global client instance
openai_client = OpenAIClient()
