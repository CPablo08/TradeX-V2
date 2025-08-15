#!/bin/bash

# TradeX Jetson Setup Script
# Complete automated setup for Jetson Orin Nano

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if running on Jetson
check_jetson() {
    if [ ! -f "/etc/nv_tegra_release" ]; then
        print_warning "This script is designed for Jetson devices. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_error "Setup cancelled."
            exit 1
        fi
    else
        print_status "Jetson device detected!"
    fi
}

# Function to check system requirements
check_system() {
    print_header "Checking System Requirements"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python3 found: $PYTHON_VERSION"
    else
        print_error "Python3 not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    fi
    
    # Check available memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -lt 4 ]; then
        print_warning "Low memory detected: ${MEMORY_GB}GB. TradeX requires at least 4GB for optimal performance."
    else
        print_status "Memory: ${MEMORY_GB}GB"
    fi
    
    # Check available disk space
    DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_GB" -lt 10 ]; then
        print_error "Insufficient disk space: ${DISK_GB}GB. Need at least 10GB."
        exit 1
    else
        print_status "Available disk space: ${DISK_GB}GB"
    fi
}

# Function to optimize Jetson performance
optimize_jetson() {
    print_header "Optimizing Jetson Performance"
    
    # Set performance mode
    if command -v nvpmodel &> /dev/null; then
        print_status "Setting performance mode..."
        sudo nvpmodel -m 0
    fi
    
    # Set max clocks
    if command -v jetson_clocks &> /dev/null; then
        print_status "Setting max clocks..."
        sudo jetson_clocks
    fi
    
    # Disable GUI for more resources (optional)
    print_warning "Disable GUI for more resources? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        sudo systemctl set-default multi-user.target
        print_status "GUI disabled. Reboot required to take effect."
    fi
}

# Function to install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    print_status "Updating package list..."
    sudo apt-get update
    
    print_status "Installing essential packages..."
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        git \
        curl \
        wget \
        htop \
        screen \
        tmux \
        nano \
        vim \
        unzip \
        software-properties-common
    
    print_status "Installing development tools..."
    sudo apt-get install -y \
        cmake \
        pkg-config \
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        libhdf5-dev \
        libhdf5-serial-dev \
        libatlas-base-dev \
        gfortran
    
    print_status "System dependencies installed successfully!"
}

# Function to setup Python environment
setup_python_env() {
    print_header "Setting Up Python Environment"
    
    # Create virtual environment
    if [ ! -d "tradex_env" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv tradex_env
    else
        print_status "Virtual environment already exists."
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source tradex_env/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install base requirements
    print_status "Installing base requirements..."
    pip install -r requirements_jetson.txt
    
    # Install TensorFlow for Jetson
    print_status "Installing TensorFlow for Jetson..."
    pip install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512 tensorflow==2.15.0+nv23.11
    
    print_status "Python environment setup complete!"
}

# Function to setup environment variables
setup_environment() {
    print_header "Setting Up Environment Variables"
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp env_example.txt .env
        
        print_warning "Please edit .env file with your Coinbase API credentials:"
        echo "1. Open .env file: nano .env"
        echo "2. Add your Coinbase API passphrase"
        echo "3. Save and exit (Ctrl+X, Y, Enter)"
        echo ""
        read -p "Press Enter when you've configured the .env file..."
    else
        print_status ".env file already exists."
    fi
}

# Function to create necessary directories
create_directories() {
    print_header "Creating Directories"
    
    mkdir -p logs
    mkdir -p models
    mkdir -p backtest_results
    mkdir -p data
    
    print_status "Directories created successfully!"
}

# Function to setup systemd service
setup_service() {
    print_header "Setting Up System Service"
    
    print_status "Creating systemd service..."
    sudo cp tradex.service /etc/systemd/system/
    
    print_status "Reloading systemd..."
    sudo systemctl daemon-reload
    
    print_status "Enabling TradeX service..."
    sudo systemctl enable tradex
    
    print_status "Service setup complete!"
    print_status "To start: sudo systemctl start tradex"
    print_status "To check status: sudo systemctl status tradex"
    print_status "To view logs: sudo journalctl -u tradex -f"
}

# Function to run tests
run_tests() {
    print_header "Running System Tests"
    
    # Activate virtual environment
    source tradex_env/bin/activate
    
    print_status "Testing basic functionality..."
    if python3 basic_test.py; then
        print_status "✅ Basic test passed!"
    else
        print_error "❌ Basic test failed!"
        return 1
    fi
    
    print_status "Testing imports..."
    if python3 minimal_test.py; then
        print_status "✅ Import test passed!"
    else
        print_error "❌ Import test failed!"
        return 1
    fi
    
    print_status "Testing API connection..."
    if python3 test_api.py; then
        print_status "✅ API test passed!"
    else
        print_warning "⚠️ API test failed - check your credentials in .env"
    fi
    
    print_status "All tests completed!"
}

# Function to show final instructions
show_final_instructions() {
    print_header "Setup Complete!"
    
    echo ""
    echo -e "${GREEN}🎉 TradeX has been successfully installed on your Jetson!${NC}"
    echo ""
    echo -e "${BLUE}Quick Start Commands:${NC}"
    echo "1. Activate environment: source tradex_env/bin/activate"
    echo "2. Train models: python3 main.py --mode train"
    echo "3. Run backtest: python3 main.py --mode backtest"
    echo "4. Paper trading: python3 main.py --mode paper"
    echo "5. Live trading: python3 start_tradex.py"
    echo ""
    echo -e "${BLUE}Service Commands:${NC}"
    echo "• Start service: sudo systemctl start tradex"
    echo "• Check status: sudo systemctl status tradex"
    echo "• View logs: sudo journalctl -u tradex -f"
    echo "• Stop service: sudo systemctl stop tradex"
    echo ""
    echo -e "${BLUE}Monitoring Commands:${NC}"
    echo "• System resources: tegrastats"
    echo "• Application logs: tail -f logs/tradex.log"
    echo "• Process status: htop"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Configure your .env file with API credentials"
    echo "2. Run: python3 main.py --mode train"
    echo "3. Test with: python3 main.py --mode paper"
    echo "4. Start live trading when ready"
    echo ""
    echo -e "${GREEN}Happy Trading! 🚀${NC}"
}

# Function to handle errors
handle_error() {
    print_error "Setup failed at step: $1"
    print_error "Error: $2"
    exit 1
}

# Main setup function
main() {
    print_header "TradeX Jetson Setup Script"
    echo "This script will install and configure TradeX on your Jetson Orin Nano"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please don't run this script as root. Run as regular user."
        exit 1
    fi
    
    # Confirm setup
    print_warning "This will install TradeX and configure your system. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled."
        exit 1
    fi
    
    # Run setup steps
    check_jetson || handle_error "Jetson Check" "Failed to verify Jetson device"
    check_system || handle_error "System Check" "System requirements not met"
    optimize_jetson || handle_error "Optimization" "Failed to optimize Jetson"
    install_system_deps || handle_error "System Dependencies" "Failed to install system packages"
    setup_python_env || handle_error "Python Setup" "Failed to setup Python environment"
    setup_environment || handle_error "Environment" "Failed to setup environment"
    create_directories || handle_error "Directories" "Failed to create directories"
    setup_service || handle_error "Service" "Failed to setup system service"
    run_tests || handle_error "Tests" "System tests failed"
    
    show_final_instructions
}

# Run main function
main "$@"
