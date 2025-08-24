# High-Level Agentic Bot Flow - Development Makefile
# Travel Agent AI with Session Management

.PHONY: help install backend frontend dev clean test health backend-logs frontend-logs stop

# Default target
help:
	@echo "🚀 Travel Agent Development Commands"
	@echo "=================================="
	@echo "make dev          - Start both backend and frontend servers"
	@echo "make backend      - Start backend server only"
	@echo "make frontend     - Start frontend server only"
	@echo "make install      - Install all dependencies"
	@echo "make health       - Check if services are running"
	@echo "make test         - Run backend tests"
	@echo "make clean        - Clean up processes and cache"
	@echo "make logs         - Show backend and frontend logs"
	@echo "make stop         - Stop all running servers"
	@echo ""

# Install all dependencies
install: install-backend install-frontend
	@echo "✅ All dependencies installed!"

install-backend:
	@echo "📦 Installing backend dependencies..."
	@cd backend && python -m venv venv || true
	@cd backend && source venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install

# Start backend server
backend:
	@echo "🔧 Starting backend server..."
	@cd backend && source venv/bin/activate && python application.py &
	@echo "⏳ Waiting for backend to be ready..."
	@sleep 3
	@$(MAKE) --no-print-directory wait-for-backend

# Wait for backend to be healthy
wait-for-backend:
	@echo "🔍 Checking backend health..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then \
			echo "✅ Backend is ready at http://localhost:8000"; \
			break; \
		fi; \
		echo "⏳ Waiting for backend... (attempt $$i/10)"; \
		sleep 2; \
	done
	@if ! curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then \
		echo "❌ Backend failed to start after 20 seconds"; \
		exit 1; \
	fi

# Start frontend server
frontend:
	@echo "🎨 Starting frontend server..."
	@cd frontend && npm run dev &
	@sleep 3
	@echo "✅ Frontend should be ready at http://localhost:3000"

# Start both servers in the correct order
dev:
	@echo "🚀 Starting Travel Agent Development Environment..."
	@echo "================================================="
	@$(MAKE) --no-print-directory stop
	@echo ""
	@$(MAKE) --no-print-directory backend
	@echo ""
	@echo "⏳ Waiting 2 seconds before starting frontend..."
	@sleep 2
	@$(MAKE) --no-print-directory frontend
	@echo ""
	@echo "🎉 Development environment is ready!"
	@echo "📍 Backend:  http://localhost:8000"
	@echo "📍 Frontend: http://localhost:3000"
	@echo "📍 API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop all servers"

# Health check for running services
health:
	@echo "🏥 Checking service health..."
	@echo "Backend Health:"
	@curl -s http://localhost:8000/api/v1/health/ | python -m json.tool 2>/dev/null || echo "❌ Backend not responding"
	@echo ""
	@echo "Frontend Health:"
	@curl -s http://localhost:3000/ > /dev/null 2>&1 && echo "✅ Frontend is running" || echo "❌ Frontend not responding"
	@echo ""
	@echo "Active Sessions:"
	@curl -s http://localhost:8000/api/v1/chat/sessions 2>/dev/null | python -c "import sys,json; data=json.load(sys.stdin); print(f'📊 {data[\"total\"]} active sessions')" 2>/dev/null || echo "❌ Cannot fetch sessions"

# Run backend tests
test:
	@echo "🧪 Running backend tests..."
	@cd backend && source venv/bin/activate && python -m pytest tests/ -v || echo "No tests found"

# Show logs (requires that servers were started with this Makefile)
logs:
	@echo "📋 Showing recent logs..."
	@echo "Backend processes:"
	@pgrep -f "python application.py" || echo "No backend process found"
	@echo ""
	@echo "Frontend processes:"
	@pgrep -f "npm run dev" || echo "No frontend process found"

# Stop all running servers
stop:
	@echo "🛑 Stopping all servers..."
	@pkill -f "python application.py" 2>/dev/null || true
	@pkill -f "npm run dev" 2>/dev/null || true
	@pkill -f "node.*vite" 2>/dev/null || true
	@sleep 1
	@echo "✅ All servers stopped"

# Clean up processes and cache files
clean: stop
	@echo "🧹 Cleaning up..."
	@cd backend && find . -name "*.pyc" -delete 2>/dev/null || true
	@cd backend && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@cd frontend && rm -rf dist/ 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Quick development restart
restart: stop dev

# Production build (for deployment)
build:
	@echo "🏗️  Building for production..."
	@cd frontend && npm run build
	@echo "✅ Production build complete"

# Show running processes
ps:
	@echo "🔍 Running processes:"
	@echo "Backend:"
	@pgrep -fl "python application.py" || echo "No backend process"
	@echo "Frontend:"
	@pgrep -fl "npm run dev" || echo "No frontend process"
	@pgrep -fl "node.*vite" || echo "No vite process"

# Development environment status
status:
	@echo "📊 Development Environment Status"
	@echo "================================="
	@$(MAKE) --no-print-directory ps
	@echo ""
	@$(MAKE) --no-print-directory health
