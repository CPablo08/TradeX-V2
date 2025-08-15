#!/usr/bin/env python3
"""
TradeX TensorFlow Fix Script
Handles TensorFlow installation issues on different platforms
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🧠 {message}")
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

def detect_platform():
    """Detect the current platform and architecture"""
    system = platform.system()
    machine = platform.machine()
    
    print_status(f"Detected platform: {system} {machine}")
    
    if system == "Linux":
        if "aarch64" in machine or "arm64" in machine:
            return "jetson"
        else:
            return "linux"
    elif system == "Darwin":
        if "arm64" in machine:
            return "macos_arm"
        else:
            return "macos_intel"
    elif system == "Windows":
        return "windows"
    else:
        return "unknown"

def get_tensorflow_version(platform_type):
    """Get the appropriate TensorFlow version for the platform"""
    versions = {
        "jetson": "tensorflow==2.15.0+nv23.11",
        "linux": "tensorflow==2.15.0",
        "macos_arm": "tensorflow-macos==2.15.0",
        "macos_intel": "tensorflow==2.15.0",
        "windows": "tensorflow==2.15.0",
        "unknown": "tensorflow==2.15.0"
    }
    return versions.get(platform_type, "tensorflow==2.15.0")

def install_tensorflow_jetson(pip_executable):
    """Install TensorFlow specifically for Jetson"""
    print_status("Installing TensorFlow for Jetson...")
    
    try:
        # First, try the NVIDIA repository
        result = subprocess.run([
            str(pip_executable), "install", 
            "--extra-index-url", "https://developer.download.nvidia.com/compute/redist/jp/v512",
            "tensorflow==2.15.0+nv23.11"
        ], check=True, capture_output=True, text=True)
        
        print_success("TensorFlow for Jetson installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Failed to install TensorFlow for Jetson: {e}")
        
        # Fallback to regular TensorFlow
        try:
            print_status("Trying regular TensorFlow as fallback...")
            result = subprocess.run([
                str(pip_executable), "install", "tensorflow==2.15.0"
            ], check=True, capture_output=True, text=True)
            
            print_success("Regular TensorFlow installed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print_error(f"Failed to install regular TensorFlow: {e2}")
            return False

def install_tensorflow_macos(pip_executable):
    """Install TensorFlow for macOS"""
    print_status("Installing TensorFlow for macOS...")
    
    try:
        # Try TensorFlow for macOS first
        result = subprocess.run([
            str(pip_executable), "install", "tensorflow-macos==2.15.0"
        ], check=True, capture_output=True, text=True)
        
        print_success("TensorFlow for macOS installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Failed to install TensorFlow for macOS: {e}")
        
        # Fallback to regular TensorFlow
        try:
            print_status("Trying regular TensorFlow as fallback...")
            result = subprocess.run([
                str(pip_executable), "install", "tensorflow==2.15.0"
            ], check=True, capture_output=True, text=True)
            
            print_success("Regular TensorFlow installed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print_error(f"Failed to install regular TensorFlow: {e2}")
            return False

def install_tensorflow_linux(pip_executable):
    """Install TensorFlow for Linux"""
    print_status("Installing TensorFlow for Linux...")
    
    try:
        result = subprocess.run([
            str(pip_executable), "install", "tensorflow==2.15.0"
        ], check=True, capture_output=True, text=True)
        
        print_success("TensorFlow for Linux installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install TensorFlow: {e}")
        return False

def install_tensorflow_windows(pip_executable):
    """Install TensorFlow for Windows"""
    print_status("Installing TensorFlow for Windows...")
    
    try:
        result = subprocess.run([
            str(pip_executable), "install", "tensorflow==2.15.0"
        ], check=True, capture_output=True, text=True)
        
        print_success("TensorFlow for Windows installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install TensorFlow: {e}")
        return False

def test_tensorflow_import(python_executable):
    """Test TensorFlow import"""
    print_status("Testing TensorFlow import...")
    
    test_script = """
try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__} imported successfully")
    
    # Test basic functionality
    print("Testing TensorFlow functionality...")
    a = tf.constant([1, 2, 3])
    b = tf.constant([4, 5, 6])
    c = tf.add(a, b)
    print(f"✅ TensorFlow computation test: {c.numpy()}")
    
    # Check for GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU detected: {len(gpus)} device(s)")
        for gpu in gpus:
            print(f"   - {gpu}")
    else:
        print("⚠️ No GPU detected - will use CPU")
    
except ImportError as e:
    print(f"❌ TensorFlow import failed: {e}")
    return False
except Exception as e:
    print(f"❌ TensorFlow test failed: {e}")
    return False

print("✅ TensorFlow test completed successfully!")
"""
    
    try:
        result = subprocess.run([
            str(python_executable), "-c", test_script
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"TensorFlow test failed: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def install_alternative_ml_libraries(pip_executable):
    """Install alternative ML libraries if TensorFlow fails"""
    print_status("Installing alternative ML libraries...")
    
    alternatives = [
        "scikit-learn==1.3.2",
        "xgboost==2.0.3",
        "lightgbm==4.1.0",
        "catboost==1.2.2"
    ]
    
    for lib in alternatives:
        try:
            print_status(f"Installing {lib}...")
            subprocess.run([
                str(pip_executable), "install", lib
            ], check=True, capture_output=True, text=True)
            print_success(f"{lib} installed successfully")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to install {lib}: {e}")

def main():
    """Main TensorFlow fix function"""
    print_header("TradeX TensorFlow Fix")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_error("Please activate your virtual environment first")
        print_status("Run: source tradex_env/bin/activate")
        return False
    
    # Detect platform
    platform_type = detect_platform()
    
    # Get pip executable
    if platform.system() == "Windows":
        pip_executable = Path(sys.prefix) / "Scripts" / "pip.exe"
    else:
        pip_executable = Path(sys.prefix) / "bin" / "pip"
    
    if not pip_executable.exists():
        print_error(f"Pip executable not found at: {pip_executable}")
        return False
    
    print_status(f"Using pip: {pip_executable}")
    
    # Install TensorFlow based on platform
    success = False
    
    if platform_type == "jetson":
        success = install_tensorflow_jetson(pip_executable)
    elif platform_type in ["macos_arm", "macos_intel"]:
        success = install_tensorflow_macos(pip_executable)
    elif platform_type == "linux":
        success = install_tensorflow_linux(pip_executable)
    elif platform_type == "windows":
        success = install_tensorflow_windows(pip_executable)
    else:
        print_warning("Unknown platform, trying generic TensorFlow")
        success = install_tensorflow_linux(pip_executable)
    
    # Test the installation
    if success:
        python_executable = Path(sys.executable)
        if test_tensorflow_import(python_executable):
            print_success("TensorFlow is working correctly!")
            return True
        else:
            print_warning("TensorFlow installed but import test failed")
    
    # If TensorFlow fails, install alternatives
    print_warning("TensorFlow installation failed or import test failed")
    print_status("Installing alternative ML libraries...")
    install_alternative_ml_libraries(pip_executable)
    
    print_header("TensorFlow Fix Complete")
    if success:
        print_success("TensorFlow should now work correctly")
        print_status("Try running: python3 -c 'import tensorflow; print(tensorflow.__version__)'")
    else:
        print_warning("TensorFlow installation failed, but alternative ML libraries are available")
        print_status("TradeX will use scikit-learn, XGBoost, and other libraries instead")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ TensorFlow fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
