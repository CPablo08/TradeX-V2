#!/usr/bin/env python3
"""
TradeX System Test Script
Tests all components to ensure everything is working correctly
"""

import sys
import os
import time
from datetime import datetime

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import tensorflow as tf
        print("✅ tensorflow imported successfully")
    except ImportError as e:
        print(f"❌ tensorflow import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ scikit-learn import failed: {e}")
        return False
    
    try:
        import xgboost as xgb
        print("✅ xgboost imported successfully")
    except ImportError as e:
        print(f"❌ xgboost import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import Config
        print("✅ Config imported successfully")
        print(f"   API Key: {'✅ Set' if Config.CB_API_KEY else '❌ Not set'}")
        print(f"   API Secret: {'✅ Set' if Config.CB_API_SECRET else '❌ Not set'}")
        print(f"   Passphrase: {'✅ Set' if Config.CB_API_PASSPHRASE else '❌ Not set'}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_data_collector():
    """Test data collector"""
    print("\n📊 Testing data collector...")
    
    try:
        from data_collector import DataCollector
        collector = DataCollector()
        print("✅ DataCollector initialized successfully")
        return True
    except Exception as e:
        print(f"❌ DataCollector test failed: {e}")
        return False

def test_ml_engine():
    """Test ML engine"""
    print("\n🧠 Testing ML engine...")
    
    try:
        from ml_engine import MLEngine
        ml_engine = MLEngine()
        print("✅ MLEngine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ MLEngine test failed: {e}")
        return False

def test_risk_manager():
    """Test risk manager"""
    print("\n🛡️ Testing risk manager...")
    
    try:
        from risk_manager import RiskManager
        risk_manager = RiskManager()
        print("✅ RiskManager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ RiskManager test failed: {e}")
        return False

def test_trading_engine():
    """Test trading engine"""
    print("\n🎯 Testing trading engine...")
    
    try:
        from trading_engine import TradingEngine
        engine = TradingEngine(paper_trading=True)
        print("✅ TradingEngine initialized successfully (paper trading mode)")
        return True
    except Exception as e:
        print(f"❌ TradingEngine test failed: {e}")
        return False

def test_backtest_engine():
    """Test backtest engine"""
    print("\n📈 Testing backtest engine...")
    
    try:
        from backtest_engine import BacktestEngine
        backtest = BacktestEngine(initial_balance=1000)
        print("✅ BacktestEngine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ BacktestEngine test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TradeX System Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_imports,
        test_config,
        test_data_collector,
        test_ml_engine,
        test_risk_manager,
        test_trading_engine,
        test_backtest_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TradeX is ready to run.")
        print("\n📋 Next steps:")
        print("   1. Run: python3 main.py --mode train")
        print("   2. Run: python3 main.py --mode backtest")
        print("   3. Run: python3 start_tradex.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Check your .env file configuration")
        print("   3. Verify API credentials in config.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
