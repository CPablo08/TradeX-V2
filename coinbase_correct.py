#!/usr/bin/env python3
"""
Correct Coinbase Advanced Trade API Implementation
Based on official documentation: https://docs.cloud.coinbase.com/advanced-trade-api/docs/rest-api-auth
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from config import Config

def test_correct_coinbase_api():
    """Test Coinbase Advanced Trade API with correct authentication"""
    print("🔍 Testing Coinbase Advanced Trade API (Correct Implementation)...")
    
    # Test 1: Public endpoint
    try:
        print("📡 Testing public endpoint...")
        response = requests.get("https://api.coinbase.com/api/v3/brokerage/products", timeout=10)
        if response.status_code == 200:
            print("✅ Public API works")
        else:
            print(f"❌ Public API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Public API error: {e}")
    
    # Test 2: Authenticated endpoint with correct method
    try:
        print("\n🔐 Testing authenticated endpoint...")
        
        # API credentials
        api_key_name = Config.CB_API_KEY_NAME
        private_key = Config.CB_PRIVATE_KEY
        
        print(f"🔑 API Key Name: {api_key_name[:50]}...")
        print(f"🔑 Private Key: [PEM format]")
        
        # According to official docs:
        # 1. Extract the private key from PEM format
        # 2. Use HMAC-SHA256 with the private key as the secret
        # 3. Sign the message: timestamp + method + request_path + body
        
        # Extract private key from PEM
        key_lines = private_key.split('\n')
        key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
        private_key_bytes = base64.b64decode(key_data)
        
        # Endpoint details
        method = 'GET'
        request_path = '/api/v3/brokerage/accounts'
        url = f"https://api.coinbase.com{request_path}"
        timestamp = str(int(time.time()))
        body = ''  # No body for GET request
        
        # Create message to sign (timestamp + method + request_path + body)
        message = timestamp + method + request_path + body
        
        print(f"📝 Message to sign: {message}")
        print(f"📝 Timestamp: {timestamp}")
        print(f"📝 Method: {method}")
        print(f"📝 Path: {request_path}")
        
        # Create HMAC signature
        signature = hmac.new(
            private_key_bytes,
            message.encode('utf-8'),
            hashlib.sha256
        )
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        
        print(f"📝 Signature: {signature_b64[:20]}...")
        
        # Headers according to official docs
        headers = {
            'CB-ACCESS-KEY': api_key_name,
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Making request to: {url}")
        print(f"📤 Headers: {json.dumps(headers, indent=2)}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        print(f"📥 Response body: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            data = response.json()
            print(f"📊 Found {len(data.get('accounts', []))} accounts")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alternative_endpoints():
    """Test alternative endpoints that might work"""
    print("\n🔧 Testing alternative endpoints...")
    
    api_key_name = Config.CB_API_KEY_NAME
    private_key = Config.CB_PRIVATE_KEY
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different endpoints
    endpoints = [
        '/api/v3/brokerage/accounts',
        '/v2/accounts',
        '/api/v3/brokerage/products',
        '/api/v3/brokerage/orders/historical/fills'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔧 Testing endpoint: {endpoint}")
            
            method = 'GET'
            timestamp = str(int(time.time()))
            body = ''
            message = timestamp + method + endpoint + body
            
            signature = hmac.new(
                private_key_bytes,
                message.encode('utf-8'),
                hashlib.sha256
            )
            signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
            
            headers = {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': signature_b64,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'Content-Type': 'application/json'
            }
            
            url = f"https://api.coinbase.com{endpoint}"
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {endpoint} works!")
                return True
            else:
                print(f"❌ {endpoint} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {endpoint} error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Coinbase Advanced Trade API Test")
    print("=" * 50)
    
    # Test correct implementation
    success = test_correct_coinbase_api()
    
    if not success:
        print("\n🔄 Trying alternative endpoints...")
        test_alternative_endpoints()
    
    print("\n📋 Summary:")
    print("- Check the response for specific error messages")
    print("- Verify your API key has the correct permissions")
    print("- Ensure your private key is in the correct format")
    print("- Check if your account is enabled for Advanced Trade API")
