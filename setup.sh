#!/bin/bash

# TradeX Setup Script
# This script sets up the TradeX trading bot platform

echo "🚀 TradeX Setup Script"
echo "======================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Create required directories
echo "📁 Creating directories..."
mkdir -p data logs
echo "✅ Directories created"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd client
npm install
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# Trading Configuration
TRADING_MODE=paper
PORT=5000

# API Keys (for real trading - optional)
# ALPACA_API_KEY=your_alpaca_api_key  # Not needed for paper trading simulation
ALPACA_SECRET_KEY=your_alpaca_secret_key
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET=your_coinbase_secret

# Database Configuration
DATABASE_PATH=./data/tradex.db

# Logging Configuration
LOG_LEVEL=info
LOG_FILE_PATH=./logs/tradex.log
EOF
    echo "✅ .env file created"
    echo "⚠️  Please update the .env file with your API keys if needed"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 TradeX setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your API keys (optional)"
echo "2. Start the backend: npm start"
echo "3. Start the frontend: cd client && npm start"
echo "4. Access the dashboard at: http://localhost:3000"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "Happy Trading! 🚀💰"
