# Travel Agent - Agentic Bot Flow

A conversational AI travel agent that demonstrates agentic bot flows with multi-step planning, memory management, and real-time updates using Server-Sent Events (SSE).

## 🚀 Quick Start

Get the entire development environment running with one command:

```bash
make dev
```

This will:
1. Start the backend server (FastAPI + MongoDB)
2. Wait for it to be ready
3. Start the frontend server (Vue.js + Vite)
4. Display URLs for both services

**That's it!** Your travel agent is ready at:
- 🎨 **Frontend**: http://localhost:3000
- 🔧 **Backend**: http://localhost:8000  
- 📚 **API Docs**: http://localhost:8000/docs

### Other Useful Commands

```bash
make help       # Show all available commands
make install    # Install all dependencies
make health     # Check service status
make stop       # Stop all servers
make clean      # Clean up processes and cache
make ps         # Show running processes
```

## 🎯 Features

### Core Capabilities
- **Intelligent Conversation**: Natural language processing for travel requests
- **Agent Orchestration**: Multi-step planning for flights, hotels, and activities
- **Memory Management**: Persistent user preferences and conversation context
- **Session Persistence**: Complete conversation history with intelligent session naming
- **Real-time Updates**: SSE-based live agent action streaming
- **Web Search Integration**: OpenAI-powered web search for current travel information
- **Contextual Responses**: Maintains conversation flow and handles clarifications

### User Experience
- **Interactive Chat Interface**: Clean, modern chat UI with typing indicators
- **Session Management**: ChatGPT-style session sidebar with intelligent naming
- **Inspector Panel**: Real-time view of agent actions, memory updates, and preferences  
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Graceful error recovery with clear user feedback

## 🏗️ Architecture

### System Overview
```
Frontend (Vue.js)
    ↕️ SSE + HTTP
Backend (FastAPI)
    ↕️ 
MongoDB Atlas + OpenAI API
```

### Backend Architecture (Python FastAPI)
```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── application.py          # Application entry point
│   ├── config/
│   │   ├── settings.py         # Environment configuration
│   │   ├── constants.py        # Application constants
│   │   └── prompts.py          # AI prompts organized by use case
│   ├── clients/
│   │   ├── openai_client.py    # OpenAI API client wrapper
│   │   └── mongodb_client.py   # MongoDB Atlas client wrapper
│   ├── core/
│   │   ├── agent.py            # Main travel agent orchestrator
│   │   ├── memory.py           # Unified memory management
│   │   ├── sse.py              # Server-sent events manager
│   │   └── schemas.py          # Pydantic models and validation
│   ├── services/
│   │   └── travel_search.py    # Travel search using OpenAI web search
│   └── routes/
│       ├── chat.py             # Chat endpoints + SSE
│       └── health.py           # Health check endpoints
└── requirements.txt
```

### Frontend Architecture (Vue.js)
```
frontend/
├── src/
│   ├── App.vue                 # Main application component
│   ├── components/
│   │   ├── ChatInterface.vue   # Chat UI with message history
│   │   ├── InspectorPanel.vue  # Real-time agent action viewer
│   │   └── SessionSidebar.vue  # Session management sidebar
│   ├── composables/
│   │   ├── useSSE.ts           # Server-sent events composable
│   │   ├── useChat.ts          # Chat state and functionality
│   │   └── useMarkdown.ts      # Markdown rendering utilities
│   ├── services/
│   │   └── api.ts              # HTTP API client
│   ├── stores/
│   │   ├── chat.ts             # Chat state management (Pinia)  
│   │   ├── sessions.ts         # Session management state
│   │   └── preferences.ts      # User preferences state
│   └── types/
│       └── index.ts            # TypeScript interfaces
└── package.json
```

## 📋 Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)
- OpenAI API key

### Backend Setup
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Update credentials in app/config/settings.py
# (MongoDB Atlas connection string and OpenAI API key are already configured)

# Run the application
python application.py

# Or for development with auto-reload
uvicorn app.main:app --reload --port 8000
```

The backend will start at `http://localhost:8000`

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start at `http://localhost:3000`

## 🤖 Agent Flow Example

### Conversation Flow
```
1. User: "Plan a 3-day trip to Tokyo for 2 people, budget ₹50000"

2. Agent Actions (via SSE):
   🧠 Analyzing intent: travel_request
   💾 Updated preferences: destination=Tokyo, budget=₹50000, people_count=2
   🔍 Searching flights to Tokyo...
   🏨 Finding hotels in Tokyo...
   🎯 Discovering Tokyo activities...
   💬 Generating travel recommendations

3. Response: Comprehensive travel plan with flights, hotels, and activities

4. User: "Actually, make the budget ₹30000"

5. Agent Actions:
   🧠 Analyzing intent: preference_update  
   💾 Updated preferences: budget=₹30000
   💬 Generating updated recommendations

6. Response: Revised travel plan within new budget
```

### Memory System
The agent remembers:
- **Travel Preferences**: Budget, destination, dates, group size, origin city
- **Dietary Requirements**: Vegetarian, allergies, special dietary needs
- **Activity Preferences**: Adventure, culture, relaxation, food experiences
- **Stay Preferences**: Hotel type, accommodation preferences
- **Conversation Context**: Complete session history and previous decisions
- **Session Metadata**: Intelligent titles, message counts, travel details

## 💬 Conversation Examples

### Example 1: Initial Trip Planning
```
User: "I want to plan a weekend getaway to Goa"

Agent: I'd love to help plan your Goa getaway! Let me gather some details to give you the best recommendations:

🔍 Searching current Goa travel information...

Based on current information, here are some great options for a Goa weekend:

✈️ **Flights**: Delhi to Goa starting from ₹8,000 return...
🏨 **Hotels**: Beach resorts from ₹3,000/night...  
🎯 **Activities**: Beach hopping, water sports, Old Goa churches...

To refine these recommendations, could you tell me:
- What's your approximate budget?
- Are you traveling solo or with others?
- Any specific interests (beaches, nightlife, culture)?
```

### Example 2: Mid-conversation Changes
```
User: "Change my budget to ₹25000 instead of ₹40000"

Agent: Got it! I've updated your budget to ₹25,000. Let me revise the recommendations to fit your new budget:

💾 Updated preferences: budget = ₹25,000

🔍 Searching budget-friendly options...

Here are the updated recommendations:
✈️ **Flights**: Budget airlines starting ₹6,500...
🏨 **Hotels**: Great value properties ₹2,000-2,500/night...
🎯 **Activities**: Free beaches, affordable local experiences...

This budget will give you a wonderful 3-day Goa experience with comfortable accommodation and great activities!
```

## 🔧 Technical Design Decisions

### 1. Server-Sent Events over WebSockets
- **Why**: Simpler implementation, better for one-way communication, auto-reconnection
- **Implementation**: Real-time agent action streaming with heartbeat mechanism
- **Benefits**: Works through firewalls, simpler deployment, less overhead

### 2. OpenAI Web Search Integration
- **Why**: Single API for both conversation and web search, consistent responses
- **Implementation**: Structured prompts for flight, hotel, and activity searches
- **Benefits**: Real-time travel information, no API key management for multiple services

### 3. MongoDB Atlas for Persistence
- **Why**: Managed service, flexible document structure, good Python integration
- **Implementation**: Separate collections for conversations and preferences
- **Benefits**: No database maintenance, automatic scaling, rich queries

### 4. Unified Memory System
- **Why**: Consistent interface for both conversation and preference storage
- **Implementation**: Single MemoryManager class with context retrieval
- **Benefits**: Simplified agent logic, consistent data access, easy testing

### 5. Agent Orchestration Pattern
- **Why**: Clear separation of concerns, extensible for new capabilities
- **Implementation**: Main agent routes to specialized services based on intent
- **Benefits**: Maintainable code, easy to add features, clear debugging

## 📊 API Documentation

### Chat Endpoints
- `POST /api/v1/chat/message` - Send chat message
- `POST /api/v1/chat/message/stream` - Send chat message with streaming response
- `GET /api/v1/chat/events/{session_id}` - SSE stream for real-time updates
- `GET /api/v1/chat/history/{session_id}` - Get conversation history
- `GET /api/v1/chat/context/{session_id}` - Get session context
- `GET /api/v1/chat/sessions` - Get all sessions
- `PUT /api/v1/chat/session/{session_id}` - Update session details
- `DELETE /api/v1/chat/session/{session_id}` - Clear session data
- `POST /api/v1/chat/preferences` - Update user preferences

### Health Endpoints  
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/database` - Database connectivity check
- `GET /api/v1/health/ready` - Readiness check for deployment

### SSE Event Types
- `response` - Agent response message
- `agent_action` - Agent action with description
- `memory_update` - Preference updates
- `typing` - Typing indicator
- `error` - Error messages
- `heartbeat` - Keep connection alive

## 🧪 Testing the Application

### Backend Testing
```bash
# Start backend
cd backend && python application.py

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "message": "Plan a trip to Goa"}'

# Test SSE endpoint
curl -N -H "Accept: text/event-stream" \
  http://localhost:8000/api/v1/chat/events/test-123
```

### Frontend Testing
```bash
# Start frontend
cd frontend && npm run dev

# Access application
open http://localhost:3000

# Test conversation examples:
1. "Plan a 3-day trip to Tokyo for ₹50000"
2. "I'm vegetarian and love cultural activities"  
3. "Change my budget to ₹30000"
4. "Show me hotel options in Mumbai"
```

## 📈 Assignment Deliverables

✅ **Working Codebase**: Complete frontend + backend + real travel search  
✅ **Clean Architecture**: Separated concerns, minimal dependencies  
✅ **Memory System**: Persistent preferences and conversation context  
✅ **Agent Actions**: Real-time streaming of multi-step processes  
✅ **Error Handling**: Graceful failures with user feedback  
✅ **SSE Integration**: Real-time updates without WebSocket complexity  
✅ **Conversation Examples**: Demonstrated initial planning + mid-flow changes  
✅ **Documentation**: Complete setup and architecture explanation  

## 🔍 Key Design Principles

1. **Minimal Complexity**: No unnecessary abstractions or over-engineering
2. **Real Functionality**: Actual OpenAI web search, not mock data
3. **Production Ready**: Proper error handling, logging, and deployment configs
4. **Clean Code**: Well-organized structure, clear naming, good separation
5. **User Focused**: Intuitive interface, clear feedback, graceful degradation
