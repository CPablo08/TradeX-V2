#!/bin/bash

# TradeX Startup Script
# This script starts the backend server, frontend server, and opens the dashboard

echo "🚀 Starting TradeX Trading Bot Platform..."
echo "=========================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for server to be ready
wait_for_server() {
    local port=$1
    local server_name=$2
    echo "⏳ Waiting for $server_name to be ready on port $port..."
    
    for i in {1..30}; do
        if check_port $port; then
            echo "✅ $server_name is ready!"
            return 0
        fi
        sleep 1
    done
    
    echo "❌ $server_name failed to start on port $port"
    return 1
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
pkill -f "node.*server" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
sleep 2

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "client" ]; then
    echo "❌ Error: Please run this script from the TradeX root directory"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing backend dependencies..."
    npm install
fi

if [ ! -d "client/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd client && npm install && cd ..
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs

# Start backend server in background
echo "🔧 Starting backend server..."
npm start > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
if wait_for_server 5000 "Backend Server"; then
    echo "✅ Backend server started successfully"
else
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend server in background
echo "🎨 Starting frontend server..."
cd client
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
if wait_for_server 3000 "Frontend Server"; then
    echo "✅ Frontend server started successfully"
else
    echo "❌ Frontend server failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

# Wait a bit more for React to fully compile
echo "⏳ Waiting for React to compile..."
sleep 5

# Open dashboard in default browser
echo "🌐 Opening dashboard in browser..."
if command -v xdg-open > /dev/null; then
    # Linux
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    # macOS
    open http://localhost:3000
elif command -v start > /dev/null; then
    # Windows
    start http://localhost:3000
else
    echo "📱 Please open your browser and go to: http://localhost:3000"
fi

echo ""
echo "🎉 TradeX is now running!"
echo "=========================================="
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📝 Backend Logs: logs/backend.log"
echo "🎨 Frontend Logs: logs/frontend.log"
echo ""
echo "💡 To stop TradeX, press Ctrl+C or run: ./stop.sh"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down TradeX..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ TradeX stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running and show logs
echo "📋 Live logs (Ctrl+C to stop):"
echo "=========================================="
tail -f logs/backend.log logs/frontend.log
