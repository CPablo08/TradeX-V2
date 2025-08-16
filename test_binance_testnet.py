#!/usr/bin/env python3
"""
Test Binance Testnet Connection
Verifies that the testnet configuration works properly
"""

import requests
import time
from datetime import datetime
from config import Config

def test_binance_testnet():
    """Test Binance testnet connectivity and basic functionality"""
    
    print("🔍 Testing Binance Testnet Connection")
    print("=" * 50)
    
    # Test 1: Check if testnet is enabled
    print(f"📊 Testnet Mode: {'✅ ENABLED' if Config.BINANCE_TESTNET else '❌ DISABLED'}")
    print(f"🌐 Base URL: {Config.BINANCE_BASE_URL}")
    print(f"🔌 WebSocket URL: {Config.BINANCE_WS_URL}")
    
    # Test 2: Test basic connectivity
    try:
        print("\n🔗 Testing basic connectivity...")
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/ping", timeout=10)
        if response.status_code == 200:
            print("✅ Basic connectivity: SUCCESS")
        else:
            print(f"❌ Basic connectivity: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Basic connectivity: ERROR - {e}")
    
    # Test 3: Test server time
    try:
        print("\n⏰ Testing server time...")
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/time", timeout=10)
        if response.status_code == 200:
            server_time = response.json()
            print(f"✅ Server time: {datetime.fromtimestamp(server_time['serverTime']/1000)}")
        else:
            print(f"❌ Server time: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server time: ERROR - {e}")
    
    # Test 4: Test exchange info
    try:
        print("\n📈 Testing exchange info...")
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/exchangeInfo", timeout=10)
        if response.status_code == 200:
            exchange_info = response.json()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'] == Config.SYMBOL]
            if symbols:
                print(f"✅ Exchange info: SUCCESS (Found {Config.SYMBOL})")
            else:
                print(f"⚠️ Exchange info: SUCCESS (But {Config.SYMBOL} not found)")
        else:
            print(f"❌ Exchange info: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Exchange info: ERROR - {e}")
    
    # Test 5: Test 24hr ticker
    try:
        print(f"\n💰 Testing 24hr ticker for {Config.SYMBOL}...")
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/ticker/24hr", 
                              params={'symbol': Config.SYMBOL}, timeout=10)
        if response.status_code == 200:
            ticker = response.json()
            print(f"✅ 24hr ticker: SUCCESS")
            print(f"   Current Price: ${float(ticker['lastPrice']):,.2f}")
            print(f"   24hr Change: {float(ticker['priceChangePercent']):+.2f}%")
            print(f"   24hr Volume: {float(ticker['volume']):,.2f}")
        else:
            print(f"❌ 24hr ticker: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ 24hr ticker: ERROR - {e}")
    
    # Test 6: Test historical klines (candlestick data)
    try:
        print(f"\n📊 Testing historical data for {Config.SYMBOL}...")
        params = {
            'symbol': Config.SYMBOL,
            'interval': '1h',
            'limit': 10
        }
        response = requests.get(f"{Config.BINANCE_BASE_URL}/api/v3/klines", 
                              params=params, timeout=10)
        if response.status_code == 200:
            klines = response.json()
            print(f"✅ Historical data: SUCCESS ({len(klines)} candles)")
            if klines:
                latest_candle = klines[-1]
                print(f"   Latest candle: {datetime.fromtimestamp(latest_candle[0]/1000)}")
                print(f"   Open: ${float(latest_candle[1]):,.2f}")
                print(f"   High: ${float(latest_candle[2]):,.2f}")
                print(f"   Low: ${float(latest_candle[3]):,.2f}")
                print(f"   Close: ${float(latest_candle[4]):,.2f}")
        else:
            print(f"❌ Historical data: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Historical data: ERROR - {e}")
    
    # Test 7: Test API key authentication (if provided)
    if Config.BINANCE_API_KEY and Config.BINANCE_SECRET_KEY:
        try:
            print(f"\n🔐 Testing API authentication...")
            # This would require HMAC signature generation
            # For now, just check if credentials are set
            print(f"✅ API Key: {'✅ SET' if Config.BINANCE_API_KEY else '❌ NOT SET'}")
            print(f"✅ Secret Key: {'✅ SET' if Config.BINANCE_SECRET_KEY else '❌ NOT SET'}")
            print("ℹ️  Note: Full authentication test requires HMAC signature generation")
        except Exception as e:
            print(f"❌ API authentication: ERROR - {e}")
    else:
        print(f"\n🔐 API authentication: SKIPPED (No credentials provided)")
        print("ℹ️  For full testing, add your testnet API credentials to .env file")
    
    print("\n" + "=" * 50)
    print("🎯 Testnet Configuration Summary:")
    print(f"   • Testnet Mode: {'✅ ENABLED' if Config.BINANCE_TESTNET else '❌ DISABLED'}")
    print(f"   • Trading Symbol: {Config.SYMBOL}")
    print(f"   • Paper Trading: {'✅ ENABLED' if Config.PAPER_TRADING else '❌ DISABLED'}")
    print(f"   • API Credentials: {'✅ SET' if Config.BINANCE_API_KEY else '❌ NOT SET'}")
    
    if Config.BINANCE_TESTNET:
        print("\n✅ Testnet is properly configured!")
        print("🔗 Get testnet API credentials from: https://testnet.binance.vision/")
        print("💡 Add credentials to .env file for full functionality")
    else:
        print("\n⚠️ Testnet is disabled - using live Binance API")
        print("🚨 Be careful - this will use real trading!")

if __name__ == "__main__":
    test_binance_testnet()
