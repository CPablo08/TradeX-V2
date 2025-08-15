#!/usr/bin/env python3
"""
Coinbase Developer Platform API Implementation
Based on official documentation: https://docs.cloud.coinbase.com/
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from config import Config

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

def test_coinbase_developer_api():
    """Test Coinbase Developer Platform API"""
    print("🔍 Testing Coinbase Developer Platform API")
    print("=" * 60)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key from PEM
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different endpoints based on Developer Platform documentation
    test_cases = [
        {
            'name': 'Accounts List',
            'method': 'GET',
            'path': '/api/v3/brokerage/accounts',
            'description': 'List all accounts'
        },
        {
            'name': 'Products List',
            'method': 'GET',
            'path': '/api/v3/brokerage/products',
            'description': 'List all products'
        },
        {
            'name': 'Product Details',
            'method': 'GET',
            'path': '/api/v3/brokerage/products/BTC-USD',
            'description': 'Get BTC-USD product details'
        },
        {
            'name': 'Account Details',
            'method': 'GET',
            'path': '/api/v3/brokerage/accounts/primary',
            'description': 'Get primary account details'
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
            
            # Headers according to Developer Platform documentation
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

def test_alternative_auth_methods():
    """Test alternative authentication methods for Developer Platform"""
    print("\n🔄 Testing Alternative Authentication Methods")
    print("=" * 50)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name or not private_key:
        return False
    
    # Extract private key
    key_lines = private_key.split('\n')
    key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
    private_key_bytes = base64.b64decode(key_data)
    
    # Test different authentication approaches
    auth_methods = [
        {
            'name': 'Standard HMAC',
            'sign_method': 'hmac'
        },
        {
            'name': 'ECDSA Signature',
            'sign_method': 'ecdsa'
        }
    ]
    
    for auth_method in auth_methods:
        try:
            print(f"\n🔧 Testing: {auth_method['name']}")
            
            method = 'GET'
            path = '/api/v3/brokerage/accounts'
            url = f"https://api.coinbase.com{path}"
            timestamp = str(int(time.time()))
            body = ''
            message = timestamp + method + path + body
            
            if auth_method['sign_method'] == 'hmac':
                # Standard HMAC
                signature = hmac.new(
                    private_key_bytes,
                    message.encode('utf-8'),
                    hashlib.sha256
                )
                signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
            elif auth_method['sign_method'] == 'ecdsa':
                # ECDSA signature (if cryptography is available)
                try:
                    from cryptography.hazmat.primitives import hashes, serialization
                    from cryptography.hazmat.primitives.asymmetric import ec
                    from cryptography.hazmat.backends import default_backend
                    
                    private_key_obj = serialization.load_pem_private_key(
                        private_key.encode('utf-8'),
                        password=None,
                        backend=default_backend()
                    )
                    
                    signature = private_key_obj.sign(
                        message.encode('utf-8'),
                        ec.ECDSA(hashes.SHA256())
                    )
                    signature_b64 = base64.b64encode(signature).decode('utf-8')
                except ImportError:
                    print("⚠️ cryptography not available, skipping ECDSA")
                    continue
            
            headers = {
                'CB-ACCESS-KEY': api_key_name,
                'CB-ACCESS-SIGN': signature_b64,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {auth_method['name']} works!")
                return True
            else:
                print(f"❌ {auth_method['name']} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ {auth_method['name']} error: {e}")
    
    return False

def check_api_permissions():
    """Check API key permissions and requirements"""
    print("\n🔍 API Key Analysis")
    print("=" * 30)
    
    api_key_name, private_key = load_credentials()
    if not api_key_name:
        return
    
    print(f"🔑 API Key Name: {api_key_name}")
    print(f"🔑 Key Format: {api_key_name.split('/')}")
    
    if 'organizations' in api_key_name:
        print("🏢 This is an organization API key from Developer Platform")
        org_id = api_key_name.split('/')[1]
        key_id = api_key_name.split('/')[3]
        print(f"🏢 Organization ID: {org_id}")
        print(f"🔑 Key ID: {key_id}")
    
    print("\n📋 Developer Platform API Requirements:")
    print("1. 🔑 Organization must be verified")
    print("2. 🔑 API key must have correct permissions")
    print("3. 🔑 Organization must have access to Advanced Trade")
    print("4. 🔑 API key must be active and not expired")
    
    print("\n💡 Solutions to try:")
    print("1. 📱 Check organization settings in Developer Platform")
    print("2. 📱 Verify organization is fully verified")
    print("3. 📱 Check API key permissions in Developer Platform")
    print("4. 📱 Ensure organization has Advanced Trade access")
    print("5. 📱 Contact Coinbase Developer Support")

if __name__ == "__main__":
    print("🚀 Coinbase Developer Platform API Test")
    print("=" * 60)
    
    # Test with Developer Platform API
    success = test_coinbase_developer_api()
    
    if not success:
        print("\n🔄 Trying alternative authentication methods...")
        test_alternative_auth_methods()
    
    # Check permissions
    check_api_permissions()
    
    print("\n📋 Next Steps:")
    print("1. Check Developer Platform organization settings")
    print("2. Verify organization permissions")
    print("3. Ensure Advanced Trade is enabled for organization")
    print("4. Contact Coinbase Developer Support if needed")
