#!/bin/bash

# TradeX Dependency Fix Script for Jetson
# Run this if you get ModuleNotFoundError

echo "🔧 TradeX Dependency Fix Script"
echo "================================"

# Check if we're in the TradeX directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the TradeX directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "tradex_env" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup_jetson.sh first"
    exit 1
fi

echo "📦 Installing missing dependencies..."

# Activate virtual environment
source tradex_env/bin/activate

# Install specific missing packages
echo "Installing loguru..."
pip install loguru==0.7.2

echo "Installing Pillow for PDF generation..."
pip install Pillow==10.0.0

echo "Installing other core dependencies..."
pip install pandas==2.1.4 numpy==1.24.3 scikit-learn==1.3.2
pip install xgboost==2.0.3 ta==0.10.2
pip install requests==2.31.0 python-dotenv==1.0.0
pip install schedule==1.2.0 psutil==5.9.6
pip install matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0
pip install joblib==1.3.2

echo "✅ Dependencies installed successfully!"
echo ""
echo "🚀 You can now run TradeX commands:"
echo "   python3 main.py --mode paper"
echo "   python3 main.py --mode backtest"
echo "   python3 main.py --mode report"
