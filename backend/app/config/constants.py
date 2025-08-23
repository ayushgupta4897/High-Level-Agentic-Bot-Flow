"""Application constants and default values"""

# Agent Actions
AGENT_ACTIONS = {
    "SEARCH_FLIGHTS": "search_flights",
    "SEARCH_HOTELS": "search_hotels", 
    "SEARCH_ACTIVITIES": "search_activities",
    "ANALYZE_INTENT": "analyze_intent",
    "UPDATE_MEMORY": "update_memory",
    "GENERATE_RESPONSE": "generate_response",
    "WEB_SEARCH": "web_search"
}

# Intent Types
INTENTS = {
    "TRAVEL_REQUEST": "travel_request",
    "PREFERENCE_UPDATE": "preference_update", 
    "CLARIFICATION": "clarification",
    "GENERAL": "general"
}

# Travel Categories
TRAVEL_CATEGORIES = {
    "FLIGHTS": "flights",
    "HOTELS": "hotels",
    "ACTIVITIES": "activities",
    "RESTAURANTS": "restaurants"
}

# Default Values
DEFAULTS = {
    "BUDGET_RANGE": (10000, 500000),  # INR
    "MAX_SEARCH_RESULTS": 5,
    "MESSAGE_HISTORY_LIMIT": 20,
    "SSE_RETRY_TIMEOUT": 3000,  # milliseconds
    "SEARCH_TIMEOUT": 30,  # seconds
}

# Error Messages
ERROR_MESSAGES = {
    "CONNECTION_FAILED": "Unable to connect. Please try again.",
    "SEARCH_FAILED": "Search failed. Please refine your request.",
    "INVALID_DESTINATION": "Please provide a valid destination.",
    "INVALID_BUDGET": "Please provide a valid budget amount.",
    "GENERAL_ERROR": "Something went wrong. Please try again."
}

# Success Messages  
SUCCESS_MESSAGES = {
    "PREFERENCES_UPDATED": "Your preferences have been updated successfully.",
    "SEARCH_COMPLETED": "Search completed successfully.",
    "MEMORY_SAVED": "Your information has been saved."
}

# Web Search Templates
SEARCH_TEMPLATES = {
    "FLIGHTS": "best flights from {origin} to {destination} in {dates} under budget {budget} INR",
    "HOTELS": "best hotels in {destination} under {budget} INR per night with good reviews", 
    "ACTIVITIES": "top things to do and activities in {destination} tourist attractions",
    "RESTAURANTS": "best restaurants in {destination} for {preferences}"
}
