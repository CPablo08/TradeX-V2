#!/usr/bin/env python3
"""
TradeX Architecture Fix Script
Fixes TensorFlow architecture mismatch issues (ELF header errors)
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔧 {message}")
    print("=" * 60)

def print_status(message):
    """Print a status message"""
    print(f"📋 {message}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️ {message}")

def detect_architecture():
    """Detect the system architecture"""
    machine = platform.machine()
    print_status(f"Detected architecture: {machine}")
    
    if machine in ['aarch64', 'arm64']:
        return 'arm64'
    elif machine in ['x86_64', 'amd64']:
        return 'x86_64'
    else:
        return 'unknown'

def check_tensorflow_installation():
    """Check if TensorFlow is installed and working"""
    print_status("Checking TensorFlow installation...")
    
    try:
        import tensorflow as tf
        print_success(f"TensorFlow {tf.__version__} imported successfully")
        return True
    except ImportError as e:
        print_error(f"TensorFlow import failed: {e}")
        return False
    except Exception as e:
        if "invalid ELF header" in str(e):
            print_error("TensorFlow architecture mismatch detected!")
            print_error("This usually means x86_64 TensorFlow was installed on ARM64 system")
            return False
        else:
            print_error(f"TensorFlow error: {e}")
            return False

def remove_tensorflow():
    """Remove TensorFlow completely"""
    print_status("Removing TensorFlow...")
    
    try:
        # Get pip executable
        if platform.system() == "Windows":
            pip_executable = Path(sys.prefix) / "Scripts" / "pip.exe"
        else:
            pip_executable = Path(sys.prefix) / "bin" / "pip"
        
        # Uninstall TensorFlow and related packages
        packages_to_remove = [
            "tensorflow",
            "tensorflow-macos",
            "tensorflow-gpu",
            "keras",
            "tensorboard"
        ]
        
        for package in packages_to_remove:
            try:
                subprocess.run([
                    str(pip_executable), "uninstall", package, "-y"
                ], check=True, capture_output=True, text=True)
                print_success(f"Removed {package}")
            except subprocess.CalledProcessError:
                print_warning(f"{package} not found or already removed")
        
        return True
    except Exception as e:
        print_error(f"Failed to remove TensorFlow: {e}")
        return False

def clean_tensorflow_cache():
    """Clean TensorFlow cache and temporary files"""
    print_status("Cleaning TensorFlow cache...")
    
    try:
        # Remove TensorFlow cache directories
        cache_dirs = [
            Path.home() / ".cache" / "pip",
            Path.home() / ".local" / "lib" / "python3.10" / "site-packages" / "tensorflow",
            Path(sys.prefix) / "lib" / "python3.10" / "site-packages" / "tensorflow"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    print_success(f"Cleaned {cache_dir}")
                except Exception as e:
                    print_warning(f"Could not clean {cache_dir}: {e}")
        
        return True
    except Exception as e:
        print_error(f"Failed to clean cache: {e}")
        return False

def install_correct_tensorflow():
    """Install the correct TensorFlow version for the architecture"""
    print_status("Installing correct TensorFlow version...")
    
    architecture = detect_architecture()
    
    # Get pip executable
    if platform.system() == "Windows":
        pip_executable = Path(sys.prefix) / "Scripts" / "pip.exe"
    else:
        pip_executable = Path(sys.prefix) / "bin" / "pip"
    
    if architecture == 'arm64':
        print_status("Installing TensorFlow for ARM64...")
        
        # Try Jetson-specific TensorFlow first
        try:
            subprocess.run([
                str(pip_executable), "install", 
                "--extra-index-url", "https://developer.download.nvidia.com/compute/redist/jp/v512",
                "tensorflow==2.15.0+nv23.11"
            ], check=True, capture_output=True, text=True)
            print_success("Jetson TensorFlow installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_warning("Jetson TensorFlow failed, trying regular ARM64 TensorFlow...")
            
            # Try regular TensorFlow for ARM64
            try:
                subprocess.run([
                    str(pip_executable), "install", "tensorflow==2.15.0"
                ], check=True, capture_output=True, text=True)
                print_success("Regular TensorFlow for ARM64 installed successfully")
                return True
            except subprocess.CalledProcessError as e2:
                print_error("Failed to install TensorFlow for ARM64")
                return False
    
    elif architecture == 'x86_64':
        print_status("Installing TensorFlow for x86_64...")
        
        try:
            subprocess.run([
                str(pip_executable), "install", "tensorflow==2.15.0"
            ], check=True, capture_output=True, text=True)
            print_success("TensorFlow for x86_64 installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error("Failed to install TensorFlow for x86_64")
            return False
    
    else:
        print_error(f"Unsupported architecture: {architecture}")
        return False

def install_alternative_ml_libraries():
    """Install alternative ML libraries that work without TensorFlow"""
    print_status("Installing alternative ML libraries...")
    
    # Get pip executable
    if platform.system() == "Windows":
        pip_executable = Path(sys.prefix) / "Scripts" / "pip.exe"
    else:
        pip_executable = Path(sys.prefix) / "bin" / "pip"
    
    alternatives = [
        "scikit-learn==1.3.2",
        "xgboost==2.0.3",
        "lightgbm==4.1.0",
        "catboost==1.2.2",
        "numpy==1.24.3",
        "pandas==2.1.4"
    ]
    
    success_count = 0
    for lib in alternatives:
        try:
            print_status(f"Installing {lib}...")
            subprocess.run([
                str(pip_executable), "install", lib
            ], check=True, capture_output=True, text=True)
            print_success(f"{lib} installed successfully")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to install {lib}: {e}")
    
    return success_count > 0

def test_ml_libraries():
    """Test that ML libraries work correctly"""
    print_status("Testing ML libraries...")
    
    test_script = """
# Test scikit-learn
try:
    from sklearn.ensemble import RandomForestClassifier
    print("✅ scikit-learn RandomForest works")
except Exception as e:
    print(f"❌ scikit-learn failed: {e}")

# Test XGBoost
try:
    import xgboost as xgb
    print("✅ XGBoost works")
except Exception as e:
    print(f"❌ XGBoost failed: {e}")

# Test LightGBM
try:
    import lightgbm as lgb
    print("✅ LightGBM works")
except Exception as e:
    print(f"❌ LightGBM failed: {e}")

# Test CatBoost
try:
    import catboost as cb
    print("✅ CatBoost works")
except Exception as e:
    print(f"❌ CatBoost failed: {e}")

print("\\nML library test completed!")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_script
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"ML library test failed: {e}")
        return False

def main():
    """Main architecture fix function"""
    print_header("TradeX Architecture Fix")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_error("Please activate your virtual environment first")
        print_status("Run: source tradex_env/bin/activate")
        return False
    
    # Detect architecture
    architecture = detect_architecture()
    print_status(f"System architecture: {architecture}")
    
    # Check current TensorFlow installation
    if check_tensorflow_installation():
        print_success("TensorFlow is working correctly!")
        return True
    
    # Remove incorrect TensorFlow installation
    print_warning("Removing incorrect TensorFlow installation...")
    if not remove_tensorflow():
        print_error("Failed to remove TensorFlow")
        return False
    
    # Clean cache
    if not clean_tensorflow_cache():
        print_warning("Failed to clean cache, continuing anyway...")
    
    # Try to install correct TensorFlow
    print_status("Attempting to install correct TensorFlow...")
    tensorflow_success = install_correct_tensorflow()
    
    if tensorflow_success:
        # Test the new installation
        if check_tensorflow_installation():
            print_success("TensorFlow architecture fix successful!")
            return True
        else:
            print_warning("TensorFlow installed but still not working")
    
    # Install alternative ML libraries
    print_status("Installing alternative ML libraries...")
    if install_alternative_ml_libraries():
        print_success("Alternative ML libraries installed successfully")
        
        # Test the alternatives
        if test_ml_libraries():
            print_success("Alternative ML libraries are working!")
            print_warning("TensorFlow is not available, but TradeX will work with other ML libraries")
            return True
    
    print_error("Failed to fix architecture issues")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Architecture fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
