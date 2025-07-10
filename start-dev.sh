#!/bin/bash

# 🏔️ Khabarovsk Forecast Buddy - Development Startup Script
# Starts both frontend and backend simultaneously

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$(pwd)"
FRONTEND_DIR="../habarovsk-forecast-buddy"
BACKEND_PORT=8000
FRONTEND_PORT=8080

echo -e "${BLUE}🏔️  Khabarovsk Forecast Buddy - Development Startup${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        echo -e "${YELLOW}💡 Kill the process or use a different port${NC}"
        return 1
    fi
    return 0
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"

    # Kill backend
    if [[ -n $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi

    # Kill frontend
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi

    echo -e "${GREEN}👋 Development environment stopped${NC}"
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

# Check if directories exist
if [[ ! -d "$FRONTEND_DIR" ]]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    echo -e "${YELLOW}💡 Make sure both repositories are in the same parent directory${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

# Check ports
check_port $BACKEND_PORT || exit 1
check_port $FRONTEND_PORT || exit 1

# Check backend dependencies
echo -e "${YELLOW}🔧 Checking backend...${NC}"
if [[ ! -f "requirements.txt" ]]; then
    echo -e "${RED}❌ Backend requirements.txt not found${NC}"
    exit 1
fi

if [[ ! -d "venv" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found, creating...${NC}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update backend dependencies
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

# Check .env file
if [[ ! -f ".env" ]]; then
    echo -e "${RED}❌ .env file not found in backend${NC}"
    echo -e "${YELLOW}💡 Copy .env.example and configure your settings${NC}"
    exit 1
fi

# Check frontend dependencies
echo -e "${YELLOW}🔧 Checking frontend...${NC}"
cd "$FRONTEND_DIR"

if [[ ! -f "package.json" ]]; then
    echo -e "${RED}❌ Frontend package.json not found${NC}"
    exit 1
fi

if [[ ! -d "node_modules" ]]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    npm install
else
    echo -e "${GREEN}✅ Frontend dependencies found${NC}"
fi

# Return to backend directory
cd "$BACKEND_DIR"

echo -e "${GREEN}✅ Prerequisites check complete${NC}"
echo ""

# Start backend
echo -e "${BLUE}🚀 Starting Backend (FastAPI)...${NC}"
echo -e "${YELLOW}   URL: http://localhost:$BACKEND_PORT${NC}"
echo -e "${YELLOW}   API Docs: http://localhost:$BACKEND_PORT/docs${NC}"

ENVIRONMENT=test uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "${YELLOW}📋 Backend log:${NC}"
    cat backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Start frontend
echo -e "${BLUE}🚀 Starting Frontend (React + Vite)...${NC}"
echo -e "${YELLOW}   URL: http://localhost:$FRONTEND_PORT${NC}"

cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > ../khabarovsk-server-dbase/frontend.log 2>&1 &
FRONTEND_PID=$!

# Return to backend directory
cd "$BACKEND_DIR"

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo -e "${YELLOW}📋 Frontend log:${NC}"
    cat frontend.log
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Show status
echo -e "${GREEN}🎉 Development environment is ready!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}📱 Frontend:${NC}    http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}⚙️  Backend:${NC}     http://localhost:$BACKEND_PORT"
echo -e "${GREEN}📚 API Docs:${NC}    http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}💾 Health:${NC}      http://localhost:$BACKEND_PORT/api/v1/health"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "${YELLOW}📋 Development Tips:${NC}"
echo -e "   • Frontend auto-reloads on file changes"
echo -e "   • Backend auto-reloads on Python file changes"
echo -e "   • Check backend.log and frontend.log for detailed logs"
echo -e "   • Press Ctrl+C to stop both services"
echo ""

# Wait for user interrupt
echo -e "${BLUE}🔄 Services running... Press Ctrl+C to stop${NC}"

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died${NC}"
        cleanup
        exit 1
    fi

    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died${NC}"
        cleanup
        exit 1
    fi

    sleep 5
done
