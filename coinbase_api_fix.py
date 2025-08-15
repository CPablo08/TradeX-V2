#!/usr/bin/env python3
"""
Coinbase Advanced Trade API Test - Based on Official Documentation
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from config import Config

def test_coinbase_api():
    """Test Coinbase Advanced Trade API using official documentation method"""
    print("🔍 Testing Coinbase Advanced Trade API...")
    
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
    
    # Test 2: Authenticated endpoint
    try:
        print("\n🔐 Testing authenticated endpoint...")
        
        # API credentials
        api_key_name = Config.CB_API_KEY_NAME
        private_key = Config.CB_PRIVATE_KEY
        
        print(f"🔑 API Key Name: {api_key_name[:50]}...")
        print(f"🔑 Private Key: [PEM format]")
        
        # Endpoint details
        method = 'GET'
        path = '/api/v3/brokerage/accounts'
        url = f"https://api.coinbase.com{path}"
        timestamp = str(int(time.time()))
        
        # Create message to sign
        message = timestamp + method + path
        
        print(f"📝 Message to sign: {message}")
        
        # Method 1: Try HMAC with base64 decoded key
        try:
            print("\n🔧 Method 1: HMAC with base64 decoded key")
            
            # Extract the key from PEM format
            key_lines = private_key.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            # Create HMAC signature
            signature = hmac.new(
                key_bytes,
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
            
            print(f"📤 Making request to: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Method 1: HMAC authentication works!")
                return True
            else:
                print(f"❌ Method 1 failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Method 1 error: {e}")
        
        # Method 2: Try raw key bytes
        try:
            print("\n🔧 Method 2: HMAC with raw key bytes")
            
            # Extract the key from PEM format and use raw bytes
            key_lines = private_key.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            # Use the raw key bytes directly
            signature = hmac.new(
                key_bytes,
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
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Method 2: Raw key bytes authentication works!")
                return True
            else:
                print(f"❌ Method 2 failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Method 2 error: {e}")
        
        # Method 3: Try with passphrase (old API format)
        try:
            print("\n🔧 Method 3: Old API format with passphrase")
            
            # Extract the key from PEM format
            key_lines = private_key.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            signature = hmac.new(
                key_bytes,
                message.encode('utf-8'),
                hashlib.sha256
            )
            signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
            
            headers = {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': signature_b64,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-PASSPHRASE': 'your_passphrase_here',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Method 3: Old API format works!")
                return True
            else:
                print(f"❌ Method 3 failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Method 3 error: {e}")
        
        # Method 4: Try different endpoint
        try:
            print("\n🔧 Method 4: Different endpoint (/v2/accounts)")
            
            # Extract the key from PEM format
            key_lines = private_key.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            # Try the old v2 endpoint
            method = 'GET'
            path = '/v2/accounts'
            url = f"https://api.coinbase.com{path}"
            message = timestamp + method + path
            
            signature = hmac.new(
                key_bytes,
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
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ Method 4: v2 endpoint works!")
                return True
            else:
                print(f"❌ Method 4 failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Method 4 error: {e}")
        
        print("\n❌ All authentication methods failed")
        return False
        
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

if __name__ == "__main__":
    test_coinbase_api()
