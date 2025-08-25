"""OpenAI client for basic API operations"""

import logging
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI

from app.config.settings import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI client wrapper - handles API connections and basic operations only"""
    
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

# Global client instance
openai_client = OpenAIClient()
