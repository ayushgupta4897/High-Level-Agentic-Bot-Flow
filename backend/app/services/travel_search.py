"""Travel search service using OpenAI web search"""

import logging
from typing import Dict, Any, Optional

from app.clients.openai_client import openai_client
from app.config.constants import SEARCH_TEMPLATES
from app.config.prompts import FLIGHT_SEARCH_PROMPT, HOTEL_SEARCH_PROMPT, ACTIVITY_SEARCH_PROMPT

logger = logging.getLogger(__name__)

class TravelSearchService:
    """Service for searching travel information using web search"""
    
    async def search_flights(self, travel_context: Dict[str, Any]) -> str:
        """Search for flights using web search"""
        
        try:
            destination = travel_context.get("destination")
            origin = travel_context.get("origin")
            budget = travel_context.get("budget")
            people_count = travel_context.get("people_count")
            dates = travel_context.get("dates")
            
            # Check for required information
            if not destination:
                return "I need to know your destination to search for flights. Where would you like to go?"
            
            if not origin:
                return "I need to know your departure city to search for flights. Where will you be flying from?"
            
            # Build search query
            query = SEARCH_TEMPLATES["FLIGHTS"].format(
                origin=origin,
                destination=destination,
                dates=dates or "flexible dates",
                budget=budget or "flexible budget"
            )
            
            # Perform web search
            search_results = await openai_client.web_search(query)
            
            # Generate structured response
            prompt = FLIGHT_SEARCH_PROMPT.format(
                origin=origin,
                destination=destination,
                people_count=people_count or "not specified",
                budget=budget or "flexible"
            )
            
            # Use search results to generate structured flight information
            messages = [
                {
                    "role": "system",
                    "content": "You are a flight search assistant. Based on web search results, provide practical flight recommendations with current prices and booking advice."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nSearch results: {search_results}"
                }
            ]
            
            response = await openai_client.chat_completion(messages, temperature=0.3)
            return response
            
        except Exception as e:
            logger.error(f"Flight search failed: {str(e)}")
            return f"Flight search temporarily unavailable. Please try searching manually for flights from {origin} to {destination}."
    
    async def search_hotels(self, travel_context: Dict[str, Any]) -> str:
        """Search for hotels using web search"""
        
        try:
            destination = travel_context.get("destination")
            budget = travel_context.get("budget")
            people_count = travel_context.get("people_count")
            dates = travel_context.get("dates")
            
            # Check for required information
            if not destination:
                return "I need to know your destination to search for hotels. Where are you planning to stay?"
            
            # Estimate hotel budget (30% of total budget, divided by nights) if budget is available
            hotel_budget_per_night = None
            if budget:
                # Assume 3 nights if no specific duration mentioned
                estimated_nights = 3
                hotel_budget_per_night = int(budget * 0.3 / estimated_nights)
            
            # Build search query
            query = SEARCH_TEMPLATES["HOTELS"].format(
                destination=destination,
                budget=hotel_budget_per_night or "flexible budget"
            )
            
            # Perform web search
            search_results = await openai_client.web_search(query)
            
            # Generate structured response
            prompt = HOTEL_SEARCH_PROMPT.format(
                destination=destination,
                people_count=people_count or "not specified",
                budget=hotel_budget_per_night or "flexible"
            )
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a hotel search assistant. Based on web search results, provide practical hotel recommendations with current prices, ratings, and booking advice."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nSearch results: {search_results}"
                }
            ]
            
            response = await openai_client.chat_completion(messages, temperature=0.3)
            return response
            
        except Exception as e:
            logger.error(f"Hotel search failed: {str(e)}")
            return f"Hotel search temporarily unavailable. Please try searching manually for hotels in {destination}."
    
    async def search_activities(self, travel_context: Dict[str, Any]) -> str:
        """Search for activities and attractions using web search"""
        
        try:
            destination = travel_context.get("destination")
            people_count = travel_context.get("people_count")
            activity_preferences = travel_context.get("activity_preferences")
            
            # Check for required information
            if not destination:
                return "I need to know your destination to search for activities. Where are you planning to visit?"
            
            # Build search query
            query = SEARCH_TEMPLATES["ACTIVITIES"].format(
                destination=destination
            )
            
            # Add preferences to search if available
            if activity_preferences and len(activity_preferences) > 0:
                query += f" {' '.join(activity_preferences)}"
            
            # Perform web search
            search_results = await openai_client.web_search(query)
            
            # Generate structured response
            prompt = ACTIVITY_SEARCH_PROMPT.format(
                destination=destination,
                people_count=people_count or "not specified"
            )
            
            if activity_preferences and len(activity_preferences) > 0:
                prompt += f"\n\nUser preferences: {', '.join(activity_preferences)}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a travel activities assistant. Based on web search results, provide practical activity recommendations with descriptions, prices, and booking information."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nSearch results: {search_results}"
                }
            ]
            
            response = await openai_client.chat_completion(messages, temperature=0.4)
            return response
            
        except Exception as e:
            logger.error(f"Activity search failed: {str(e)}")
            return f"Activity search temporarily unavailable. Please try searching manually for activities in {destination}."
    
    async def search_restaurants(self, travel_context: Dict[str, Any]) -> str:
        """Search for restaurants using web search"""
        
        try:
            destination = travel_context.get("destination")
            dietary_preferences = travel_context.get("dietary_preferences")
            
            # Check for required information
            if not destination:
                return "I need to know your destination to search for restaurants. Where are you planning to dine?"
            
            # Build search query
            preferences_text = " ".join(dietary_preferences) if dietary_preferences and len(dietary_preferences) > 0 else "popular"
            query = SEARCH_TEMPLATES["RESTAURANTS"].format(
                destination=destination,
                preferences=preferences_text
            )
            
            # Perform web search
            search_results = await openai_client.web_search(query)
            
            # Generate structured response
            dietary_info = ", ".join(dietary_preferences) if dietary_preferences and len(dietary_preferences) > 0 else "None specified"
            messages = [
                {
                    "role": "system",
                    "content": "You are a restaurant recommendation assistant. Based on web search results, provide practical restaurant recommendations with cuisine types, prices, and location information."
                },
                {
                    "role": "user",
                    "content": f"Recommend restaurants in {destination}. Dietary preferences: {dietary_info}\n\nSearch results: {search_results}"
                }
            ]
            
            response = await openai_client.chat_completion(messages, temperature=0.4)
            return response
            
        except Exception as e:
            logger.error(f"Restaurant search failed: {str(e)}")
            return f"Restaurant search temporarily unavailable. Please try searching manually for restaurants in {destination}."
