#!/usr/bin/env python3
"""
TradeX Virtual Environment Setup Script
Dedicated script for creating and configuring the virtual environment
"""

import os
import sys
import subprocess
import platform
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
    print(f"⚠️  {message}")

def check_python_version():
    """Check if Python version is compatible"""
    print_status("Checking Python version...")
    
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required")
        return False
    
    print_success("Python version is compatible")
    return True

def check_venv_module():
    """Check if venv module is available"""
    print_status("Checking venv module...")
    
    try:
        import venv
        print_success("venv module is available")
        return True
    except ImportError:
        print_error("venv module not found. Please install python3-venv")
        return False

def get_venv_path():
    """Get the path for the virtual environment"""
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / "tradex_env"
    return venv_path

def create_virtual_environment(venv_path):
    """Create the virtual environment"""
    print_status("Creating virtual environment...")
    
    if venv_path.exists():
        print_warning("Virtual environment already exists")
        response = input("   Do you want to recreate it? (y/N): ").strip().lower()
        if response != 'y':
            print_status("Using existing virtual environment")
            return True
        else:
            print_status("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
    
    try:
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True, capture_output=True, text=True)
        
        print_success("Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def get_python_executable(venv_path):
    """Get the Python executable path for the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def get_pip_executable(venv_path):
    """Get the pip executable path for the virtual environment"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def upgrade_pip(pip_executable):
    """Upgrade pip in the virtual environment"""
    print_status("Upgrading pip...")
    
    try:
        subprocess.run([
            str(pip_executable), "install", "--upgrade", "pip", "setuptools", "wheel"
        ], check=True, capture_output=True, text=True)
        
        print_success("pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to upgrade pip: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def install_dependencies(pip_executable, requirements_file):
    """Install dependencies from requirements file"""
    print_status(f"Installing dependencies from {requirements_file}...")
    
    if not Path(requirements_file).exists():
        print_error(f"Requirements file not found: {requirements_file}")
        return False
    
    try:
        # Install dependencies with verbose output
        result = subprocess.run([
            str(pip_executable), "install", "-r", requirements_file
        ], check=True, capture_output=True, text=True)
        
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def install_tensorflow_jetson(pip_executable):
    """Install TensorFlow specifically for Jetson"""
    print_status("Installing TensorFlow for Jetson...")
    
    try:
        result = subprocess.run([
            str(pip_executable), "install", 
            "--extra-index-url", "https://developer.download.nvidia.com/compute/redist/jp/v512",
            "tensorflow==2.15.0+nv23.11"
        ], check=True, capture_output=True, text=True)
        
        print_success("TensorFlow for Jetson installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Failed to install TensorFlow for Jetson: {e}")
        
        # Try regular TensorFlow as fallback
        try:
            print_status("Trying regular TensorFlow as fallback...")
            result = subprocess.run([
                str(pip_executable), "install", "tensorflow==2.15.0"
            ], check=True, capture_output=True, text=True)
            
            print_success("Regular TensorFlow installed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print_warning(f"Failed to install regular TensorFlow: {e2}")
            print("   TensorFlow installation failed, but TradeX will work with other ML libraries")
            return True  # Don't fail the setup for this

def test_imports(python_executable):
    """Test that key imports work"""
    print_status("Testing imports...")
    
    test_script = """
import sys
print(f"Python executable: {sys.executable}")

# Test core imports
try:
    import pandas
    print("✅ pandas")
except ImportError as e:
    print(f"❌ pandas: {e}")

try:
    import numpy
    print("✅ numpy")
except ImportError as e:
    print(f"❌ numpy: {e}")

try:
    import loguru
    print("✅ loguru")
except ImportError as e:
    print(f"❌ loguru: {e}")

try:
    import sklearn
    print("✅ scikit-learn")
except ImportError as e:
    print(f"❌ scikit-learn: {e}")

try:
    import xgboost
    print("✅ xgboost")
except ImportError as e:
    print(f"❌ xgboost: {e}")

try:
    import requests
    print("✅ requests")
except ImportError as e:
    print(f"❌ requests: {e}")

try:
    import tensorflow
    print("✅ tensorflow")
except ImportError as e:
    print(f"⚠️ tensorflow: {e}")
    print("   TradeX will use alternative ML libraries")

try:
    from PIL import Image
    print("✅ Pillow")
except ImportError as e:
    print(f"❌ Pillow: {e}")

print("\\nImport test completed!")
"""
    
    try:
        result = subprocess.run([
            str(python_executable), "-c", test_script
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Import test failed: {e}")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        return False

def create_activation_script(venv_path):
    """Create a simple activation script"""
    print_status("Creating activation script...")
    
    script_content = f"""#!/bin/bash
# TradeX Virtual Environment Activation Script
echo "🔧 Activating TradeX virtual environment..."
source "{venv_path}/bin/activate"
echo "✅ Virtual environment activated!"
echo "🚀 You can now run TradeX commands:"
echo "   python3 main.py --mode train"
echo "   python3 main.py --mode backtest"
echo "   python3 main.py --mode paper"
echo "   python3 test_system.py"
"""
    
    activation_script = Path("activate_tradex.sh")
    with open(activation_script, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    activation_script.chmod(0o755)
    
    print_success("Activation script created: activate_tradex.sh")
    return True

def main():
    """Main setup function"""
    print_header("TradeX Virtual Environment Setup")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.executable}")
    print(f"Working directory: {Path.cwd()}")
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Check venv module
    if not check_venv_module():
        return False
    
    # Step 3: Get virtual environment path
    venv_path = get_venv_path()
    print_status(f"Virtual environment path: {venv_path}")
    
    # Step 4: Create virtual environment
    if not create_virtual_environment(venv_path):
        return False
    
    # Step 5: Get executable paths
    python_executable = get_python_executable(venv_path)
    pip_executable = get_pip_executable(venv_path)
    
    print_status(f"Python executable: {python_executable}")
    print_status(f"Pip executable: {pip_executable}")
    
    # Step 6: Upgrade pip
    if not upgrade_pip(pip_executable):
        return False
    
    # Step 7: Install dependencies
    # Try Jetson requirements first, fall back to regular requirements
    requirements_files = ["requirements_jetson.txt", "requirements.txt"]
    requirements_installed = False
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            if install_dependencies(pip_executable, req_file):
                requirements_installed = True
                break
    
    if not requirements_installed:
        print_error("No requirements file found")
        return False
    
    # Step 8: Install TensorFlow for Jetson (if applicable)
    install_tensorflow_jetson(pip_executable)
    
    # Step 9: Test imports
    if not test_imports(python_executable):
        print_warning("Some imports failed, but setup may still work")
    
    # Step 10: Create activation script
    create_activation_script(venv_path)
    
    # Success!
    print_header("Setup Complete!")
    print_success("Virtual environment is ready!")
    print("\n📋 Next steps:")
    print("   1. Activate the environment:")
    print("      source tradex_env/bin/activate")
    print("   2. Or use the activation script:")
    print("      ./activate_tradex.sh")
    print("   3. Run TradeX commands:")
    print("      python3 main.py --mode train")
    print("      python3 main.py --mode backtest")
    print("      python3 test_system.py")
    print("\n💡 Note: All TradeX scripts now automatically activate the virtual environment!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
