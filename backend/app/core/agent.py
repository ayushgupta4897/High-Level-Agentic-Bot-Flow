"""Main agent orchestrator for travel planning conversations"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.clients.openai_client import openai_client
from app.core.memory import MemoryManager
from app.core.sse import sse_manager
from app.config.constants import INTENTS, AGENT_ACTIONS, SEARCH_TEMPLATES
from app.services.travel_search import TravelSearchService

logger = logging.getLogger(__name__)

class TravelAgent:
    """Main travel planning agent orchestrator"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = MemoryManager(session_id)
        self.travel_search = TravelSearchService()
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and orchestrate response"""
        
        try:
            # Save user message
            await self.memory.save_message("user", message)
            
            # Send typing indicator
            await sse_manager.send_typing(self.session_id, True)
            
            # Get context
            context = await self.memory.get_context()
            
            # Send agent action
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["ANALYZE_INTENT"],
                "Analyzing your message and understanding your travel needs"
            )
            
            # Analyze intent
            analysis = await openai_client.analyze_intent(message, context)
            
            # Process based on intent
            if analysis["intent"] == INTENTS["TRAVEL_REQUEST"]:
                response = await self._handle_travel_request(analysis, context)
            
            elif analysis["intent"] == INTENTS["PREFERENCE_UPDATE"]:
                response = await self._handle_preference_update(analysis, context)
            
            elif analysis["intent"] == INTENTS["CLARIFICATION"]:
                response = await self._handle_clarification(message, context)
            
            else:
                response = await self._handle_general_message(message, context)
            
            # Save assistant response
            await self.memory.save_message("assistant", response)
            
            # Send response
            await sse_manager.send_response(self.session_id, response)
            
            # Stop typing
            await sse_manager.send_typing(self.session_id, False)
            
            return {
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "intent": analysis["intent"]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await sse_manager.send_typing(self.session_id, False)
            await sse_manager.send_error(
                self.session_id, 
                "I apologize, I encountered an error. Please try again."
            )
            raise
    
    async def process_message_stream(self, message: str):
        """Process user message with streaming response (ChatGPT-like)"""
        
        try:
            # Save user message
            await self.memory.save_message("user", message)
            
            # Send initial events
            yield json.dumps({"type": "start", "message": "Processing your request..."})
            
            # Get context
            context = await self.memory.get_context()
            
            # Send agent action
            yield json.dumps({"type": "action", "description": "Analyzing your travel request"})
            
            # Analyze intent
            analysis = await openai_client.analyze_intent(message, context)
            
            # Extract and update preferences from ANY message (not just travel requests)
            entities = analysis["entities"]
            preferences_to_update = {}
            
            # Extract preferences from entities
            for key in ["destination", "origin", "budget", "people_count", "dates", "preferences"]:
                if entities.get(key):
                    pref_key = "activity_preferences" if key == "preferences" else key
                    preferences_to_update[pref_key] = entities[key]
            
            # Also extract preferences using OpenAI for better accuracy
            additional_prefs = await openai_client.extract_preferences(message, context)
            if additional_prefs:
                preferences_to_update.update(additional_prefs)
            
            # Send memory updates if any preferences found
            if preferences_to_update:
                updates = await self.memory.update_preferences(preferences_to_update)
                yield json.dumps({"type": "memory", "updates": updates})
                yield json.dumps({"type": "action", "description": f"Updated preferences: {', '.join(updates.keys())}"})
                
            # Perform searches if we have a destination
            travel_context = await self.memory.get_travel_context()
            search_results = {}
            
            if travel_context.get("destination") and analysis["intent"] == INTENTS["TRAVEL_REQUEST"]:
                destination = travel_context["destination"]
                yield json.dumps({"type": "action", "description": f"Searching for flights to {destination}"})
                search_results["flights"] = await self.travel_search.search_flights(travel_context)
                
                yield json.dumps({"type": "action", "description": f"Finding hotels in {destination}"})
                search_results["hotels"] = await self.travel_search.search_hotels(travel_context)
                
                yield json.dumps({"type": "action", "description": f"Discovering activities in {destination}"})
                search_results["activities"] = await self.travel_search.search_activities(travel_context)
            
            # Generate streaming response
            yield json.dumps({"type": "response_start", "message": "Generating your travel recommendations..."})
            
            full_response = ""
            async for chunk in openai_client.generate_response_stream(message, context, search_results if search_results else None):
                full_response += chunk
                # Use json.dumps to properly escape the content
                yield json.dumps({"type": "token", "content": chunk})
            
            # Save complete response
            await self.memory.save_message("assistant", full_response)
            
            # Send completion event
            yield json.dumps({"type": "complete", "timestamp": datetime.utcnow().isoformat()})
            
        except Exception as e:
            logger.error(f"Error in streaming message: {str(e)}")
            yield json.dumps({"type": "error", "message": "Sorry, I encountered an error. Please try again."})
    
    async def _handle_travel_request(
        self, 
        analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Handle travel planning requests"""
        
        entities = analysis["entities"]
        
        # Update preferences from entities
        preferences_to_update = {}
        
        if entities.get("destination"):
            preferences_to_update["destination"] = entities["destination"]
        
        if entities.get("origin"):
            preferences_to_update["origin"] = entities["origin"]
        
        if entities.get("budget"):
            preferences_to_update["budget"] = entities["budget"]
        
        if entities.get("people_count"):
            preferences_to_update["people_count"] = entities["people_count"]
        
        if entities.get("dates"):
            preferences_to_update["dates"] = entities["dates"]
        
        if entities.get("preferences"):
            preferences_to_update["activity_preferences"] = entities["preferences"]
        
        # Save preferences
        if preferences_to_update:
            updates = await self.memory.update_preferences(preferences_to_update)
            await sse_manager.send_memory_update(self.session_id, updates)
            
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["UPDATE_MEMORY"],
                f"Updated preferences: {', '.join(updates.keys())}"
            )
        
        # Get updated travel context
        travel_context = await self.memory.get_travel_context()
        
        # Perform travel searches
        search_results = {}
        
        if travel_context.get("destination"):
            # Search flights
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["SEARCH_FLIGHTS"],
                f"Searching for flights to {travel_context['destination']}"
            )
            
            flight_results = await self.travel_search.search_flights(travel_context)
            search_results["flights"] = flight_results
            
            # Search hotels
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["SEARCH_HOTELS"],
                f"Finding hotels in {travel_context['destination']}"
            )
            
            hotel_results = await self.travel_search.search_hotels(travel_context)
            search_results["hotels"] = hotel_results
            
            # Search activities
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["SEARCH_ACTIVITIES"],
                f"Discovering activities in {travel_context['destination']}"
            )
            
            activity_results = await self.travel_search.search_activities(travel_context)
            search_results["activities"] = activity_results
        
        # Generate response
        await sse_manager.send_agent_action(
            self.session_id,
            AGENT_ACTIONS["GENERATE_RESPONSE"],
            "Generating travel recommendations"
        )
        
        response = await openai_client.generate_response(
            analysis.get("original_message", ""),
            context,
            search_results
        )
        
        return response
    
    async def _handle_preference_update(
        self, 
        analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Handle preference updates"""
        
        entities = analysis["entities"]
        
        # Extract preferences to update
        preferences = await openai_client.extract_preferences(
            analysis.get("original_message", ""),
            context
        )
        
        if preferences:
            updates = await self.memory.update_preferences(preferences)
            
            await sse_manager.send_memory_update(self.session_id, updates)
            await sse_manager.send_agent_action(
                self.session_id,
                AGENT_ACTIONS["UPDATE_MEMORY"],
                f"Updated preferences: {', '.join(updates.keys())}"
            )
        
        # Generate confirmation response
        from app.config.prompts import PREFERENCE_UPDATE_PROMPT
        
        response = await openai_client.generate_response(
            analysis.get("original_message", ""),
            context,
            f"Preferences updated: {preferences}"
        )
        
        return response
    
    async def _handle_clarification(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> str:
        """Handle clarification questions"""
        
        await sse_manager.send_agent_action(
            self.session_id,
            AGENT_ACTIONS["GENERATE_RESPONSE"],
            "Answering your question"
        )
        
        response = await openai_client.generate_response(message, context)
        return response
    
    async def _handle_general_message(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> str:
        """Handle general conversation"""
        
        await sse_manager.send_agent_action(
            self.session_id,
            AGENT_ACTIONS["GENERATE_RESPONSE"],
            "Generating response"
        )
        
        response = await openai_client.generate_response(message, context)
        return response
