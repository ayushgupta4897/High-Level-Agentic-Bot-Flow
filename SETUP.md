# Travel Agent - Setup Instructions

## 🚀 Quick Start Guide

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd High-Level-Agentic-Bot-Flow
```

### 2. Backend Setup (FastAPI)
```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify configuration (credentials already set)
python -c "from app.config.settings import settings; print('✅ Settings loaded successfully')"

# Run the backend
python -m app.main
```

**Backend will be available at**: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### 3. Frontend Setup (Vue.js)
```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at**: `http://localhost:3000`

### 4. Test the Application
1. Open browser to `http://localhost:3000`
2. Try these example conversations:
   - "Plan a 3-day trip to Tokyo for ₹50000"
   - "Find hotels in Mumbai under ₹3000 per night"
   - "I'm vegetarian and want cultural activities"
   - "Change my budget to ₹25000"

## 🔧 Configuration Details

### Key Features to Test:
1. **Agent Actions**: Watch the Inspector Panel for real-time agent actions
2. **Memory Updates**: See how preferences are saved and updated
3. **Error Handling**: Try invalid requests to see graceful error handling
4. **SSE Connection**: Real-time updates without page refresh
5. **Conversation Context**: Agent remembers previous messages

## 📊 System Architecture

The application demonstrates:
- **Agentic Flow**: Multi-step travel planning with decision making
- **Memory Management**: Persistent user preferences and conversation history
- **Real-time Updates**: Server-sent events for live agent actions
- **Web Search**: OpenAI-powered search for current travel information
- **Conversation Handling**: Natural language understanding and generation

## 🚢 Deployment

### Backend (AWS Beanstalk)
```bash
cd backend
zip -r travel-agent-backend.zip . -x "*.git*" "*__pycache__*"
# Upload to Beanstalk with Python 3.9 platform
```

## 🐛 Troubleshooting

### Common Issues:
1. **Backend won't start**: Check Python version (3.9+) and dependencies
2. **MongoDB connection**: Verify network access to MongoDB Atlas
3. **OpenAI errors**: Check API key validity and usage limits
4. **SSE not working**: Ensure backend is running and CORS is configured
5. **Frontend build fails**: Check Node.js version (18+)

### Logs:
- Backend: Console output shows detailed request/response logs
- Frontend: Browser DevTools → Console for client-side logs
- SSE: DevTools → Network → EventStream for real-time connection

## 📝 Assignment Checklist

✅ **Working Demo**: Both frontend and backend operational  
✅ **Agentic Behavior**: Multi-step travel planning with decision making  
✅ **Memory System**: Preferences and conversation context persistence  
✅ **Real-time Updates**: SSE for live agent action streaming  
✅ **Error Handling**: Graceful failures with user feedback  
✅ **Clean Code**: Minimal, well-organized codebase  
✅ **Documentation**: Complete setup and architecture docs  
✅ **Conversation Examples**: Initial planning + mid-flow changes  

## 💡 Demo Script

### Conversation Flow 1: Initial Planning
```
User: "Plan a weekend trip to Goa for 2 people with ₹20000 budget"
→ Watch agent actions: Intent analysis → Memory update → Web search → Response
```

### Conversation Flow 2: Preference Changes
```
User: "Actually make that ₹30000 and I'm vegetarian"  
→ Watch memory updates and revised recommendations
```

### Inspector Panel Features:
- **Actions Tab**: Real-time agent operations
- **Memory Tab**: Stored preferences and updates  
- **Context Tab**: Session information and capabilities

This demonstrates a complete agentic bot system suitable for production use!
