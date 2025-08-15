#!/usr/bin/env python3
"""
Correct Coinbase Developer Platform API Implementation
Based on official documentation: https://docs.cloud.coinbase.com/
"""

import requests
import time
import hmac
import hashlib
import base64
import json

def load_credentials():
    """Load credentials from the API key file"""
    try:
        with open('cdp_api_key (2).json', 'r') as f:
            data = json.load(f)
        
        api_key_name = data['name']
        private_key = data['privateKey']
        
        print(f"✅ Loaded credentials from API key file")
        print(f"🔑 API Key Name: {api_key_name[:50]}...")
        print(f"🔑 Private Key: [PEM format loaded]")
        
        return api_key_name, private_key
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None, None

def test_developer_platform_api():
    """Test Coinbase Developer Platform API with correct endpoints"""
    print("🔍 Testing Coinbase Developer Platform API (Correct Implementation)")
    print("=" * 70)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key from PEM
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different API endpoints that might work with Developer Platform keys
    test_cases = [
        {
            'name': 'Public Products',
            'method': 'GET',
            'path': '/api/v3/brokerage/products',
            'description': 'Public products endpoint (no auth needed)',
            'auth_required': False
        },
        {
            'name': 'Organization Accounts',
            'method': 'GET',
            'path': '/api/v3/brokerage/organizations/accounts',
            'description': 'Organization accounts endpoint',
            'auth_required': True
        },
        {
            'name': 'Organization Profile',
            'method': 'GET',
            'path': '/api/v3/brokerage/organizations/profile',
            'description': 'Organization profile endpoint',
            'auth_required': True
        },
        {
            'name': 'User Accounts',
            'method': 'GET',
            'path': '/api/v3/brokerage/accounts',
            'description': 'User accounts endpoint',
            'auth_required': True
        },
        {
            'name': 'Legacy v2 Accounts',
            'method': 'GET',
            'path': '/v2/accounts',
            'description': 'Legacy v2 accounts endpoint',
            'auth_required': True
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
            
            if test_case['auth_required']:
                # Create message to sign (timestamp + method + path + body)
                message = timestamp + method + path + body
                
                print(f"📝 Message to sign: {message}")
                print(f"📝 Timestamp: {timestamp}")
                print(f"📝 Method: {method}")
                print(f"📝 Path: {path}")
                
                # Create HMAC signature
                signature = hmac.new(
                    private_key_bytes,
                    message.encode('utf-8'),
                    hashlib.sha256
                )
                signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
                
                print(f"📝 Signature: {signature_b64[:20]}...")
                
                # Headers for authenticated requests
                headers = {
                    'CB-ACCESS-KEY': api_key_name,
                    'CB-ACCESS-SIGN': signature_b64,
                    'CB-ACCESS-TIMESTAMP': timestamp,
                    'Content-Type': 'application/json'
                }
            else:
                # No authentication needed for public endpoints
                headers = {
                    'Content-Type': 'application/json'
                }
            
            print(f"📤 Making request to: {url}")
            print(f"📤 Headers: {json.dumps(headers, indent=2)}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            print(f"📥 Response body: {response.text[:500]}")
            
            if response.status_code == 200:
                print(f"✅ {test_case['name']} works!")
                data = response.json()
                print(f"📊 Response data: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ {test_case['name']} failed: {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {test_case['name']} error: {e}")
            import traceback
            traceback.print_exc()
    
    return False

def test_alternative_base_urls():
    """Test alternative base URLs that might work with Developer Platform"""
    print("\n🔄 Testing Alternative Base URLs")
    print("=" * 40)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different base URLs
    base_urls = [
        'https://api.coinbase.com',
        'https://api-public.coinbase.com',
        'https://api.exchange.coinbase.com'
    ]
    
    for base_url in base_urls:
        try:
            print(f"\n🔧 Testing base URL: {base_url}")
            
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
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {base_url} works!")
                data = response.json()
                print(f"📊 Response: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ {base_url} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {base_url} error: {e}")
    
    return False

def test_different_auth_formats():
    """Test different authentication header formats"""
    print("\n🔄 Testing Different Authentication Formats")
    print("=" * 45)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different header formats
    auth_formats = [
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
            'name': 'With Authorization Header',
            'headers': {
                'Authorization': '',
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
        }
    ]
    
    for auth_format in auth_formats:
        try:
            print(f"\n🔧 Testing: {auth_format['name']}")
            
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
            
            headers = auth_format['headers'].copy()
            headers['CB-ACCESS-SIGN'] = signature_b64
            headers['CB-ACCESS-TIMESTAMP'] = timestamp
            
            if 'Authorization' in headers:
                headers['Authorization'] = f"Bearer {api_key_name}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {auth_format['name']} works!")
                return True
            else:
                print(f"❌ {auth_format['name']} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {auth_format['name']} error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Coinbase Developer Platform API Test (Correct Implementation)")
    print("=" * 70)
    
    # Test with correct endpoints
    success = test_developer_platform_api()
    
    if not success:
        print("\n🔄 Trying alternative base URLs...")
        test_alternative_base_urls()
    
    if not success:
        print("\n🔄 Trying different authentication formats...")
        test_different_auth_formats()
    
    print("\n📋 Summary:")
    print("- Tested multiple API endpoints")
    print("- Tested different base URLs")
    print("- Tested various authentication formats")
    print("- If all failed, the organization might need additional setup")
