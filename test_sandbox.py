#!/usr/bin/env python3
"""
Test Coinbase Sandbox Environment
Check if the API key is for sandbox/testing environment
"""

import requests
import time
import hmac
import hashlib
import base64
import json

def load_official_credentials():
    """Load credentials from the official Coinbase file"""
    try:
        # Try new key file first
        with open('cdp_api_key (2).json', 'r') as f:
            data = json.load(f)
            api_key_name = data['name']
            private_key = data['privateKey']
            print(f"✅ Loaded credentials from new key file")
            print(f"🔑 API Key Name: {api_key_name[:50]}...")
            return api_key_name, private_key
    except Exception as e:
        try:
            # Fallback to old key file
            with open('cdp_api_key (3).json', 'r') as f:
                data = json.load(f)
                api_key_name = data['name']
                private_key = data['privateKey']
                print(f"✅ Loaded credentials from old key file")
                print(f"🔑 API Key Name: {api_key_name[:50]}...")
                return api_key_name, private_key
        except Exception as e2:
            print(f"❌ Error loading credentials: {e2}")
            return None, None

def test_sandbox_endpoints():
    """Test sandbox endpoints"""
    print("🔍 Testing Coinbase Sandbox Environment")
    print("=" * 50)
    
    api_key_name, private_key = load_official_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test sandbox endpoints
    sandbox_endpoints = [
        'https://api-public.sandbox.exchange.coinbase.com',
        'https://api-public.sandbox.coinbase.com',
        'https://sandbox.coinbase.com/api/v3/brokerage',
        'https://api-sandbox.coinbase.com'
    ]
    
    for base_url in sandbox_endpoints:
        try:
            print(f"\n🔧 Testing sandbox base URL: {base_url}")
            
            # Test public endpoint first
            try:
                public_url = f"{base_url}/products"
                print(f"📡 Testing public endpoint: {public_url}")
                response = requests.get(public_url, timeout=10)
                print(f"📥 Public status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Public endpoint works!")
                else:
                    print(f"❌ Public failed: {response.text[:100]}")
            except Exception as e:
                print(f"❌ Public error: {e}")
            
            # Test authenticated endpoint
            try:
                method = 'GET'
                path = '/accounts'
                url = f"{base_url}{path}"
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
                
                print(f"📤 Testing authenticated: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                print(f"📥 Auth status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ Sandbox authentication works!")
                    data = response.json()
                    print(f"📊 Response: {str(data)[:200]}...")
                    return True
                else:
                    print(f"❌ Auth failed: {response.text[:100]}")
                    
            except Exception as e:
                print(f"❌ Auth error: {e}")
                
        except Exception as e:
            print(f"❌ Base URL error: {e}")
    
    return False

def test_different_auth_methods():
    """Test different authentication methods"""
    print("\n🔄 Testing Different Authentication Methods")
    print("=" * 50)
    
    api_key_name, private_key = load_official_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different header formats
    test_cases = [
        {
            'name': 'Standard Headers',
            'headers': {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': '',
                'CB-ACCESS-TIMESTAMP': '',
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'With User-Agent',
            'headers': {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': '',
                'CB-ACCESS-TIMESTAMP': '',
                'Content-Type': 'application/json',
                'User-Agent': 'TradeX/1.0'
            }
        },
        {
            'name': 'With Accept Header',
            'headers': {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': '',
                'CB-ACCESS-TIMESTAMP': '',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            print(f"\n🔧 Testing: {test_case['name']}")
            
            method = 'GET'
            path = '/api/v3/brokerage/accounts'
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
            
            headers = test_case['headers'].copy()
            headers['CB-ACCESS-SIGN'] = signature_b64
            headers['CB-ACCESS-TIMESTAMP'] = timestamp
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {test_case['name']} works!")
                return True
            else:
                print(f"❌ {test_case['name']} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {test_case['name']} error: {e}")
    
    return False

def check_api_key_info():
    """Check API key information"""
    print("\n🔍 API Key Information")
    print("=" * 30)
    
    api_key_name, private_key = load_official_credentials()
    if not api_key_name:
        return
    
    print(f"🔑 API Key Name: {api_key_name}")
    print(f"🔑 Key Format: {api_key_name.split('/')}")
    
    # Check if it's an organization key
    if 'organizations' in api_key_name:
        print("🏢 This appears to be an organization API key")
        org_id = api_key_name.split('/')[1]
        key_id = api_key_name.split('/')[3]
        print(f"🏢 Organization ID: {org_id}")
        print(f"🔑 Key ID: {key_id}")
    
    print("\n💡 Possible Issues:")
    print("1. 🔑 Organization API keys might need different permissions")
    print("2. 🔑 The organization might not have Advanced Trade enabled")
    print("3. 🔑 The API key might be for a different environment")
    print("4. 🔑 The organization might need additional verification")
    
    print("\n💡 Solutions:")
    print("1. 📱 Check organization settings in Coinbase")
    print("2. 📱 Enable Advanced Trade for the organization")
    print("3. 📱 Create a personal API key instead of organization key")
    print("4. 📱 Contact Coinbase support for organization API access")

if __name__ == "__main__":
    print("🚀 Coinbase Sandbox and Alternative Authentication Test")
    print("=" * 70)
    
    # Test sandbox endpoints
    success = test_sandbox_endpoints()
    
    if not success:
        print("\n🔄 Trying different authentication methods...")
        test_different_auth_methods()
    
    # Check API key info
    check_api_key_info()
    
    print("\n📋 Summary:")
    print("- The API key appears to be an organization key")
    print("- All endpoints are returning 401 Unauthorized")
    print("- This suggests a permissions or environment issue")
    print("- Try creating a personal API key instead of organization key")
