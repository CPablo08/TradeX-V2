#!/bin/bash

# TradeX Stop Script
# This script stops all TradeX processes

echo "🛑 Stopping TradeX Trading Bot Platform..."
echo "=========================================="

# Kill backend processes
echo "🔧 Stopping backend server..."
pkill -f "node.*server" 2>/dev/null

# Kill frontend processes
echo "🎨 Stopping frontend server..."
pkill -f "react-scripts" 2>/dev/null

# Kill any remaining node processes related to TradeX
echo "🧹 Cleaning up remaining processes..."
pkill -f "TradeX" 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Check if processes are still running
if pgrep -f "node.*server" > /dev/null; then
    echo "⚠️  Some backend processes may still be running"
else
    echo "✅ Backend server stopped"
fi

if pgrep -f "react-scripts" > /dev/null; then
    echo "⚠️  Some frontend processes may still be running"
else
    echo "✅ Frontend server stopped"
fi

echo ""
echo "🎉 TradeX has been stopped!"
echo "=========================================="
echo "💡 To start TradeX again, run: ./start.sh"
