#!/usr/bin/env python3
"""
Simple test to identify where the system hangs
"""

print("1. Starting simple test...")

try:
    print("2. Importing os...")
    import os
    print("✅ os imported")
    
    print("3. Importing config...")
    from config import Config
    print("✅ config imported")
    
    print("4. Checking API credentials...")
    print(f"API Key: {Config.CB_API_KEY[:30]}...")
    print(f"API Secret: {Config.CB_API_SECRET[:30]}...")
    print(f"Passphrase: {Config.CB_API_PASSPHRASE}")
    print("✅ credentials loaded")
    
    print("5. Testing basic imports...")
    import pandas as pd
    print("✅ pandas imported")
    
    import numpy as np
    print("✅ numpy imported")
    
    print("6. Testing requests...")
    import requests
    print("✅ requests imported")
    
    print("7. Testing simple API call...")
    response = requests.get("https://httpbin.org/get", timeout=5)
    print(f"✅ Simple request works: {response.status_code}")
    
    print("8. Testing Coinbase public API...")
    response = requests.get("https://api.coinbase.com/v2/currencies", timeout=10)
    print(f"✅ Coinbase public API works: {response.status_code}")
    
    print("\n🎉 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
