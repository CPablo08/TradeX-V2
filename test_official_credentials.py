#!/usr/bin/env python3
"""
Test Official Coinbase Credentials
Uses the exact format from the downloaded API key file
"""

import requests
import time
import hmac
import hashlib
import base64
import json
import os

def load_official_credentials():
    """Load credentials from the official Coinbase file"""
    try:
        with open('cdp_api_key (3).json', 'r') as f:
            data = json.load(f)
        
        api_key_name = data['name']
        private_key = data['privateKey']
        
        print(f"✅ Loaded credentials from official file")
        print(f"🔑 API Key Name: {api_key_name[:50]}...")
        print(f"🔑 Private Key: [PEM format loaded]")
        
        return api_key_name, private_key
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None, None

def test_coinbase_advanced_trade():
    """Test Coinbase Advanced Trade API with official credentials"""
    print("🔍 Testing Coinbase Advanced Trade API with Official Credentials")
    print("=" * 70)
    
    # Load official credentials
    api_key_name, private_key = load_official_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Test 1: Public endpoint
    try:
        print("\n📡 Testing public endpoint...")
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
        
        # Extract private key from PEM
        key_lines = private_key.split('\n')
        key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
        private_key_bytes = base64.b64decode(key_data)
        
        # Endpoint details
        method = 'GET'
        request_path = '/api/v3/brokerage/accounts'
        url = f"https://api.coinbase.com{request_path}"
        timestamp = str(int(time.time()))
        body = ''
        
        # Create message to sign
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
        
        # Headers
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

def test_alternative_authentication():
    """Test alternative authentication methods"""
    print("\n🔄 Testing Alternative Authentication Methods")
    print("=" * 50)
    
    api_key_name, private_key = load_official_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different endpoints and methods
    test_cases = [
        {
            'name': 'Advanced Trade Accounts',
            'method': 'GET',
            'path': '/api/v3/brokerage/accounts',
            'description': 'Main accounts endpoint'
        },
        {
            'name': 'Advanced Trade Products',
            'method': 'GET', 
            'path': '/api/v3/brokerage/products',
            'description': 'Products endpoint'
        },
        {
            'name': 'Legacy v2 Accounts',
            'method': 'GET',
            'path': '/v2/accounts',
            'description': 'Legacy accounts endpoint'
        },
        {
            'name': 'Advanced Trade Orders',
            'method': 'GET',
            'path': '/api/v3/brokerage/orders/historical/fills',
            'description': 'Historical fills endpoint'
        }
    ]
    
    for test_case in test_cases:
        try:
            print(f"\n🔧 Testing: {test_case['name']}")
            print(f"📝 Description: {test_case['description']}")
            
            method = test_case['method']
            path = test_case['path']
            url = f"https://api.coinbase.com{path}"
            timestamp = str(int(time.time()))
            body = ''
            message = timestamp + method + path + body
            
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
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {test_case['name']} works!")
                data = response.json()
                print(f"📊 Response data: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ {test_case['name']} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {test_case['name']} error: {e}")
    
    return False

def check_api_permissions():
    """Check what permissions the API key might have"""
    print("\n🔍 Checking API Permissions")
    print("=" * 30)
    
    print("📋 Common Coinbase API Permission Issues:")
    print("1. 🔑 API key might not have 'View' permissions")
    print("2. 🔑 API key might not have 'Trade' permissions") 
    print("3. 🔑 Account might not be enabled for Advanced Trade")
    print("4. 🔑 API key might be for different environment (sandbox vs production)")
    print("5. 🔑 Account might need additional verification")
    
    print("\n💡 Solutions to try:")
    print("1. 📱 Log into Coinbase and check API key permissions")
    print("2. 📱 Enable Advanced Trade for your account")
    print("3. 📱 Verify your account is fully verified")
    print("4. 📱 Check if you need to enable specific trading permissions")
    print("5. 📱 Try creating a new API key with full permissions")

if __name__ == "__main__":
    print("🚀 Coinbase Advanced Trade API Test with Official Credentials")
    print("=" * 70)
    
    # Test with official credentials
    success = test_coinbase_advanced_trade()
    
    if not success:
        print("\n🔄 Trying alternative endpoints...")
        test_alternative_authentication()
    
    # Check permissions
    check_api_permissions()
    
    print("\n📋 Next Steps:")
    print("1. Check your Coinbase account settings")
    print("2. Verify API key permissions in Coinbase")
    print("3. Ensure Advanced Trade is enabled")
    print("4. Check if account verification is complete")
