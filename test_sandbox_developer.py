#!/usr/bin/env python3
"""
Test Sandbox Environment for Developer Platform API
Check if the API key is for sandbox/testing environment
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

def test_sandbox_environment():
    """Test if this is a sandbox environment"""
    print("🔍 Testing Sandbox Environment")
    print("=" * 40)
    
    api_key_name, private_key = load_credentials()
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
        'https://sandbox.coinbase.com',
        'https://api-sandbox.coinbase.com'
    ]
    
    for base_url in sandbox_endpoints:
        try:
            print(f"\n🔧 Testing sandbox: {base_url}")
            
            # Test public endpoint first
            try:
                public_url = f"{base_url}/products"
                print(f"📡 Testing public: {public_url}")
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

def test_developer_platform_specific():
    """Test Developer Platform specific endpoints"""
    print("\n🔍 Testing Developer Platform Specific Endpoints")
    print("=" * 50)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test Developer Platform specific endpoints
    dev_endpoints = [
        {
            'name': 'Developer Platform Profile',
            'path': '/api/v3/brokerage/organizations/profile',
            'description': 'Organization profile endpoint'
        },
        {
            'name': 'Developer Platform Settings',
            'path': '/api/v3/brokerage/organizations/settings',
            'description': 'Organization settings endpoint'
        },
        {
            'name': 'Developer Platform Users',
            'path': '/api/v3/brokerage/organizations/users',
            'description': 'Organization users endpoint'
        }
    ]
    
    for endpoint in dev_endpoints:
        try:
            print(f"\n🔧 Testing: {endpoint['name']}")
            print(f"📝 Description: {endpoint['description']}")
            
            method = 'GET'
            path = endpoint['path']
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
                print(f"✅ {endpoint['name']} works!")
                data = response.json()
                print(f"📊 Response: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ {endpoint['name']} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {endpoint['name']} error: {e}")
    
    return False

def check_organization_status():
    """Check organization status and requirements"""
    print("\n🔍 Organization Status Check")
    print("=" * 35)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name:
        return
    
    print(f"🔑 API Key Name: {api_key_name}")
    
    if 'organizations' in api_key_name:
        print("🏢 This is a Developer Platform organization API key")
        org_id = api_key_name.split('/')[1]
        key_id = api_key_name.split('/')[3]
        print(f"🏢 Organization ID: {org_id}")
        print(f"🔑 Key ID: {key_id}")
    
    print("\n📋 Possible Issues:")
    print("1. 🏢 Organization not fully verified")
    print("2. 🔑 API key permissions not set correctly")
    print("3. 🏢 Organization doesn't have Advanced Trade access")
    print("4. 🔑 API key might be for sandbox environment")
    print("5. 🏢 Organization needs additional setup")
    
    print("\n💡 Solutions:")
    print("1. 📱 Log into Developer Platform")
    print("2. 📱 Check organization verification status")
    print("3. 📱 Verify API key permissions")
    print("4. 📱 Enable Advanced Trade for organization")
    print("5. 📱 Contact Coinbase Developer Support")

if __name__ == "__main__":
    print("🚀 Sandbox Environment Test for Developer Platform")
    print("=" * 60)
    
    # Test sandbox environment
    success = test_sandbox_environment()
    
    if not success:
        print("\n🔄 Testing Developer Platform specific endpoints...")
        test_developer_platform_specific()
    
    # Check organization status
    check_organization_status()
    
    print("\n📋 Summary:")
    print("- Tested sandbox environments")
    print("- Tested Developer Platform specific endpoints")
    print("- If all failed, organization needs additional setup")
    print("- Contact Coinbase Developer Support for assistance")
