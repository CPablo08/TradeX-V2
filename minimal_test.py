#!/usr/bin/env python3
"""
Minimal test to identify the hanging issue
"""

print("🚀 Starting minimal test...")

# Test 1: Basic Python
print("✅ Python is working")

# Test 2: Basic imports
try:
    import os
    print("✅ os imported")
except Exception as e:
    print(f"❌ os import failed: {e}")

try:
    import sys
    print("✅ sys imported")
except Exception as e:
    print(f"❌ sys import failed: {e}")

try:
    import json
    print("✅ json imported")
except Exception as e:
    print(f"❌ json import failed: {e}")

try:
    import time
    print("✅ time imported")
except Exception as e:
    print(f"❌ time import failed: {e}")

# Test 3: Config import
try:
    print("📁 Trying to import config...")
    from config import Config
    print("✅ config imported")
    print(f"   API Key: {Config.CB_API_KEY[:20]}...")
    print(f"   API Secret: {Config.CB_API_SECRET[:20]}...")
except Exception as e:
    print(f"❌ config import failed: {e}")

# Test 4: Data science imports
try:
    print("📊 Trying to import pandas...")
    import pandas as pd
    print("✅ pandas imported")
except Exception as e:
    print(f"❌ pandas import failed: {e}")

try:
    print("📈 Trying to import numpy...")
    import numpy as np
    print("✅ numpy imported")
except Exception as e:
    print(f"❌ numpy import failed: {e}")

# Test 5: ML imports (these might be the problem)
try:
    print("🤖 Trying to import sklearn...")
    from sklearn.ensemble import RandomForestClassifier
    print("✅ sklearn imported")
except Exception as e:
    print(f"❌ sklearn import failed: {e}")

try:
    print("🚀 Trying to import xgboost...")
    import xgboost as xgb
    print("✅ xgboost imported")
except Exception as e:
    print(f"❌ xgboost import failed: {e}")

try:
    print("🧠 Trying to import tensorflow...")
    import tensorflow as tf
    print("✅ tensorflow imported")
except Exception as e:
    print(f"❌ tensorflow import failed: {e}")

# Test 6: Network imports
try:
    print("🌐 Trying to import requests...")
    import requests
    print("✅ requests imported")
except Exception as e:
    print(f"❌ requests import failed: {e}")

print("\n🎉 Minimal test completed!")
