#!/usr/bin/env python3
"""
Simple API test for Coinbase
"""

import requests
import time
import hmac
import hashlib
import base64
import json
from config import Config

def test_api_connection():
    """Test basic API connection"""
    print("🔍 Testing Coinbase API connection...")
    
    # Test 1: Simple public endpoint
    try:
        print("📡 Testing public endpoint...")
        response = requests.get("https://api.coinbase.com/v2/currencies", timeout=10)
        if response.status_code == 200:
            print("✅ Public API works")
        else:
            print(f"❌ Public API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Public API error: {e}")
    
    # Test 2: Check our credentials
    print(f"\n🔑 API Key Name: {Config.CB_API_KEY_NAME[:20]}...")
    print(f"🔑 Private Key: [PEM format]")
    print(f"🔑 API Type: Advanced Trade (ECDSA signature)")
    
    # Test 3: Try to make a simple authenticated request
    try:
        print("\n🔐 Testing authenticated request...")
        
        # Use a simpler endpoint first
        url = "https://api.coinbase.com/v2/accounts"
        timestamp = str(int(time.time()))
        method = 'GET'
        path = '/v2/accounts'
        
        # Create signature using private key
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend
            
            # Load the private key
            private_key = serialization.load_pem_private_key(
                Config.CB_PRIVATE_KEY.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            
            # Create the message to sign
            message = timestamp + method + path
            
            # Sign the message
            signature = private_key.sign(
                message.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
        except ImportError:
            # Fallback to HMAC if cryptography not available
            print("⚠️ cryptography library not available, using HMAC fallback")
            message = timestamp + method + path
            # Extract the key from the PEM format
            key_lines = Config.CB_PRIVATE_KEY.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            signature = hmac.new(
                key_bytes,
                message.encode('utf-8'),
                hashlib.sha256
            )
            signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        
        headers = {
            'CB-ACCESS-KEY': Config.CB_API_KEY_NAME,
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📥 Response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Authenticated API works!")
            data = response.json()
            print(f"📊 Found {len(data.get('data', []))} accounts")
        else:
            print(f"❌ API failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Authenticated API error: {e}")

if __name__ == "__main__":
    test_api_connection()
