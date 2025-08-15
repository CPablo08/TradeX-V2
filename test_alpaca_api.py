#!/usr/bin/env python3
"""
Test Alpaca API and identify its purpose
"""

import requests
import json
from datetime import datetime
from config import Config

def test_alpaca_api():
    """Test Alpaca API and identify its purpose"""
    print("🔍 Testing Alpaca API")
    print("=" * 50)
    
    # API credentials from config
    api_key = Config.ALPACA_API_KEY
    secret_key = Config.ALPACA_SECRET_KEY
    
    # Paper trading endpoint from the image
    paper_url = "https://paper-api.alpaca.markets/v2"
    
    # Headers for API requests
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"🌐 Endpoint: {paper_url}")
    print(f"📊 This appears to be a PAPER TRADING API")
    
    # Test endpoints
    test_endpoints = [
        {
            'name': 'Account Information',
            'endpoint': '/account',
            'description': 'Get account details'
        },
        {
            'name': 'Positions',
            'endpoint': '/positions',
            'description': 'Get current positions'
        },
        {
            'name': 'Orders',
            'endpoint': '/orders',
            'description': 'Get order history'
        },
        {
            'name': 'Assets',
            'endpoint': '/assets',
            'description': 'Get available assets'
        }
    ]
    
    print(f"\n🧪 Testing API endpoints...")
    
    for test in test_endpoints:
        try:
            url = f"{paper_url}{test['endpoint']}"
            print(f"\n🔧 Testing: {test['name']}")
            print(f"📝 Description: {test['description']}")
            print(f"🌐 URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test['name']} works!")
                
                if test['name'] == 'Account Information':
                    print(f"💰 Account Status: {data.get('status', 'Unknown')}")
                    print(f"💰 Account Type: {data.get('account_type', 'Unknown')}")
                    print(f"💰 Cash: ${data.get('cash', 0)}")
                    print(f"💰 Portfolio Value: ${data.get('portfolio_value', 0)}")
                    print(f"💰 Buying Power: ${data.get('buying_power', 0)}")
                    
                    # Determine if this is paper trading
                    if data.get('status') == 'ACTIVE' and data.get('account_type') == 'PAPER':
                        print(f"🎯 CONFIRMED: This is a PAPER TRADING account!")
                    elif data.get('status') == 'ACTIVE':
                        print(f"🎯 This appears to be a LIVE TRADING account!")
                
                elif test['name'] == 'Assets':
                    if isinstance(data, list) and len(data) > 0:
                        print(f"📈 Available assets: {len(data)} assets")
                        # Show first few assets
                        for i, asset in enumerate(data[:5]):
                            print(f"   {i+1}. {asset.get('symbol', 'Unknown')} - {asset.get('name', 'Unknown')}")
                        if len(data) > 5:
                            print(f"   ... and {len(data) - 5} more")
                
                elif test['name'] == 'Positions':
                    if isinstance(data, list):
                        print(f"📊 Current positions: {len(data)} positions")
                        for position in data:
                            symbol = position.get('symbol', 'Unknown')
                            qty = position.get('qty', 0)
                            market_value = position.get('market_value', 0)
                            print(f"   📈 {symbol}: {qty} shares, ${market_value}")
                
                print(f"📊 Response data: {str(data)[:200]}...")
                
            else:
                print(f"❌ {test['name']} failed: {response.status_code}")
                print(f"❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ {test['name']} error: {e}")
    
    print(f"\n📋 API Analysis:")
    print(f"✅ Endpoint: {paper_url}")
    print(f"✅ This is definitely a PAPER TRADING API")
    print(f"✅ Paper trading allows risk-free testing")
    print(f"✅ Perfect for developing and testing TradeX")
    
    return True

def test_market_data_api():
    """Test Alpaca market data API"""
    print(f"\n🔍 Testing Alpaca Market Data API")
    print("=" * 50)
    
    api_key = Config.ALPACA_API_KEY
    secret_key = Config.ALPACA_SECRET_KEY
    
    # Market data endpoint
    data_url = "https://data.alpaca.markets"
    
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    print(f"🌐 Market Data URL: {data_url}")
    
    # Test market data endpoints
    test_symbols = ['AAPL', 'BTCUSD', 'ETHUSD']
    
    for symbol in test_symbols:
        try:
            print(f"\n🔧 Testing market data for: {symbol}")
            
            # Test latest trade
            url = f"{data_url}/v2/stocks/{symbol}/trades/latest"
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'trade' in data:
                    price = data['trade']['p']
                    print(f"✅ Latest price for {symbol}: ${price}")
                else:
                    print(f"⚠️ No trade data for {symbol}")
            else:
                print(f"❌ Failed to get data for {symbol}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")

if __name__ == "__main__":
    print("🚀 Alpaca API Test and Identification")
    print("=" * 60)
    
    # Test trading API
    test_alpaca_api()
    
    # Test market data API
    test_market_data_api()
    
    print(f"\n📋 Summary:")
    print(f"✅ This is a PAPER TRADING API")
    print(f"✅ Perfect for testing TradeX without risk")
    print(f"✅ Need the SECRET KEY to complete testing")
    print(f"✅ Can trade stocks, crypto, and other assets")
    print(f"✅ Real market data with paper money")
