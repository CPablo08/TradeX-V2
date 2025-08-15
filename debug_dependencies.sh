#!/bin/bash

# TradeX Debug Script - Comprehensive dependency checker and fixer
echo "🔍 TradeX Debug Script"
echo "======================"

# Check current directory
echo "📁 Current directory: $(pwd)"
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in TradeX directory. Please cd to the TradeX folder first."
    exit 1
fi

# Check Python version
echo "🐍 Python version:"
python3 --version

# Check if virtual environment exists
if [ ! -d "tradex_env" ]; then
    echo "❌ Virtual environment not found!"
    echo "📦 Creating virtual environment..."
    python3 -m venv tradex_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source tradex_env/bin/activate

# Check if we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Failed to activate virtual environment!"
    exit 1
else
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
fi

# Check pip version
echo "📦 Pip version:"
pip --version

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies with verbose output
echo "📦 Installing dependencies..."
echo "Installing loguru..."
pip install loguru==0.7.2 -v

echo "Installing other core packages..."
pip install pandas==2.1.4 numpy==1.24.3 scikit-learn==1.3.2 -v
pip install xgboost==2.0.3 ta==0.10.2 -v
pip install requests==2.31.0 python-dotenv==1.0.0 -v
pip install schedule==1.2.0 psutil==5.9.6 -v
pip install matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0 -v
pip install Pillow==10.0.0 joblib==1.3.2 -v

# Test import
echo "🧪 Testing imports..."
python3 -c "
try:
    import loguru
    print('✅ loguru imported successfully')
except ImportError as e:
    print(f'❌ loguru import failed: {e}')

try:
    import pandas
    print('✅ pandas imported successfully')
except ImportError as e:
    print(f'❌ pandas import failed: {e}')

try:
    import numpy
    print('✅ numpy imported successfully')
except ImportError as e:
    print(f'❌ numpy import failed: {e}')

try:
    import sklearn
    print('✅ scikit-learn imported successfully')
except ImportError as e:
    print(f'❌ scikit-learn import failed: {e}')

try:
    import xgboost
    print('✅ xgboost imported successfully')
except ImportError as e:
    print(f'❌ xgboost import failed: {e}')

try:
    import ta
    print('✅ ta imported successfully')
except ImportError as e:
    print(f'❌ ta import failed: {e}')

try:
    import requests
    print('✅ requests imported successfully')
except ImportError as e:
    print(f'❌ requests import failed: {e}')

try:
    import schedule
    print('✅ schedule imported successfully')
except ImportError as e:
    print(f'❌ schedule import failed: {e}')

try:
    import psutil
    print('✅ psutil imported successfully')
except ImportError as e:
    print(f'❌ psutil import failed: {e}')

try:
    import matplotlib
    print('✅ matplotlib imported successfully')
except ImportError as e:
    print(f'❌ matplotlib import failed: {e}')

try:
    import seaborn
    print('✅ seaborn imported successfully')
except ImportError as e:
    print(f'❌ seaborn import failed: {e}')

try:
    import plotly
    print('✅ plotly imported successfully')
except ImportError as e:
    print(f'❌ plotly import failed: {e}')

try:
    from PIL import Image
    print('✅ Pillow imported successfully')
except ImportError as e:
    print(f'❌ Pillow import failed: {e}')

try:
    import joblib
    print('✅ joblib imported successfully')
except ImportError as e:
    print(f'❌ joblib import failed: {e}')
"

echo ""
echo "🎯 Now try running your command:"
echo "   python3 main.py --mode train"
echo ""
echo "💡 If you still get errors, try:"
echo "   1. Make sure you're in the virtual environment (you should see (tradex_env) in your prompt)"
echo "   2. Run: source tradex_env/bin/activate"
echo "   3. Then run your command again"
