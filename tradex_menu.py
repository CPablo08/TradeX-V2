#!/usr/bin/env python3
"""
TradeX Unified Menu System
A comprehensive terminal menu for all TradeX functions and commands
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import time

def activate_virtual_environment():
    """Automatically activate virtual environment if not already activated"""
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True  # Already in virtual environment
    
    # Check if virtual environment exists
    venv_path = Path(__file__).parent / "tradex_env"
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("📦 Please run setup first")
        return False
    
    # Get the path to the virtual environment's Python executable
    if platform.system() == "Windows":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    if not python_path.exists():
        print(f"❌ Python executable not found at: {python_path}")
        return False
    
    # If we're not in the virtual environment, restart with the virtual environment's Python
    if sys.executable != str(python_path):
        print("🔄 Activating virtual environment...")
        os.execv(str(python_path), [str(python_path)] + sys.argv)
    
    return True

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header():
    """Print the TradeX header"""
    print("=" * 70)
    print("🚀 TradeX - Crypto Trading Automation Platform")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.executable}")
    print(f"Directory: {Path.cwd()}")
    print("=" * 70)

def print_menu(title, options):
    """Print a formatted menu"""
    print(f"\n📋 {title}")
    print("-" * 50)
    for i, (key, description) in enumerate(options.items(), 1):
        print(f"{i:2d}. {key}")
        print(f"    {description}")
    print("0. Back/Exit")

def get_user_choice(max_options):
    """Get user choice with validation"""
    while True:
        try:
            choice = input(f"\n🎯 Enter your choice (0-{max_options}): ").strip()
            choice_num = int(choice)
            if 0 <= choice_num <= max_options:
                return choice_num
            else:
                print(f"❌ Please enter a number between 0 and {max_options}")
        except ValueError:
            print("❌ Please enter a valid number")

def run_command(command, description):
    """Run a command with user confirmation"""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        print("Executing...")
        try:
            result = subprocess.run(command, shell=True, check=True)
            print("✅ Command completed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
        except KeyboardInterrupt:
            print("\n❌ Command interrupted by user")
    else:
        print("❌ Command cancelled")

def setup_menu():
    """Setup and installation menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Virtual Environment Setup": "Create and configure virtual environment with all dependencies",
            "Jetson Setup": "Complete automated setup for Jetson Orin Nano",
            "Fix Dependencies": "Fix missing dependencies and import issues",
            "Fix TensorFlow": "Fix TensorFlow installation issues specifically",
            "Fix Architecture Issues": "Fix TensorFlow architecture mismatch (ELF header errors)",
            "Debug Dependencies": "Comprehensive dependency checker and fixer",
            "Check System Status": "Verify system requirements and current status"
        }
        
        print_menu("Setup & Installation", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            run_command("python3 setup_venv.py", "Setting up virtual environment...")
        elif choice == 2:
            run_command("./setup_jetson.sh", "Running Jetson setup...")
        elif choice == 3:
            run_command("./fix_dependencies.sh", "Fixing dependencies...")
        elif choice == 4:
            run_command("python3 fix_tensorflow.py", "Fixing TensorFlow installation...")
        elif choice == 5:
            run_command("python3 fix_architecture.py", "Fixing architecture issues...")
        elif choice == 6:
            run_command("./debug_dependencies.sh", "Debugging dependencies...")
        elif choice == 7:
            check_system_status()
        
        input("\nPress Enter to continue...")

def testing_menu():
    """Testing and validation menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "System Test": "Comprehensive test of all TradeX components",
            "Basic Test": "Quick functionality test",
            "API Test": "Test Binance API connection",
            "Import Test": "Test all Python imports",
            "Configuration Test": "Verify configuration settings"
        }
        
        print_menu("Testing & Validation", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            run_command("python3 test_system.py", "Running comprehensive system test...")
        elif choice == 2:
            run_command("python3 basic_test.py", "Running basic test...")
        elif choice == 3:
            run_command("python3 test_api.py", "Testing API connection...")
        elif choice == 4:
            run_command("python3 -c \"import loguru, pandas, numpy, sklearn, xgboost, tensorflow; print('✅ All imports successful')\"", "Testing imports...")
        elif choice == 5:
            check_configuration()
        
        input("\nPress Enter to continue...")

def training_menu():
    """Machine learning training menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Train Models": "Train all ML models with historical data",
            "Train Ensemble": "Train ensemble models (Random Forest, XGBoost)",
            "Train LSTM": "Train LSTM neural network model",
            "View Training Status": "Check training progress and results",
            "Training Configuration": "Configure training parameters"
        }
        
        print_menu("Machine Learning Training", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            run_command("python3 main.py --mode train", "Training all ML models...")
        elif choice == 2:
            run_command("python3 train_models.py", "Training ensemble models...")
        elif choice == 3:
            print("⚠️ LSTM training is included in the main training process")
        elif choice == 4:
            check_training_status()
        elif choice == 5:
            show_training_config()
        
        input("\nPress Enter to continue...")

def trading_menu():
    """Trading operations menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Paper Trading": "Start paper trading (simulated with real data)",
            "Live Trading": "Start live trading with real money",
            "Start with Monitor": "Start trading with automatic monitoring",
            "Trading Status": "Check current trading status",
            "Stop Trading": "Stop all trading operations"
        }
        
        print_menu("Trading Operations", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            run_command("python3 main.py --mode paper", "Starting paper trading...")
        elif choice == 2:
            confirm_live_trading()
        elif choice == 3:
            run_command("python3 start_tradex.py", "Starting trading with monitoring...")
        elif choice == 4:
            check_trading_status()
        elif choice == 5:
            stop_trading()
        
        input("\nPress Enter to continue...")

def backtesting_menu():
    """Backtesting menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Quick Backtest": "Run backtest with default settings ($1000, last month)",
            "Custom Backtest": "Run backtest with custom parameters",
            "Backtest Results": "View previous backtest results",
            "Backtest Configuration": "Configure backtest parameters",
            "Compare Strategies": "Compare different trading strategies"
        }
        
        print_menu("Backtesting", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            run_command("python3 main.py --mode backtest", "Running quick backtest...")
        elif choice == 2:
            custom_backtest()
        elif choice == 3:
            show_backtest_results()
        elif choice == 4:
            show_backtest_config()
        elif choice == 5:
            print("⚠️ Strategy comparison feature coming soon")
        
        input("\nPress Enter to continue...")

def reporting_menu():
    """Reporting and analytics menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Generate PDF Report": "Create comprehensive PDF report with graphs",
            "Performance Analytics": "View trading performance metrics",
            "System Health Report": "Generate system health and status report",
            "Log Analysis": "Analyze trading logs and events",
            "Export Data": "Export trading data for external analysis"
        }
        
        print_menu("Reporting & Analytics", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            custom_report_generation()
        elif choice == 2:
            show_performance_analytics()
        elif choice == 3:
            generate_system_report()
        elif choice == 4:
            analyze_logs()
        elif choice == 5:
            export_data()
        
        input("\nPress Enter to continue...")

def maintenance_menu():
    """System maintenance menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "System Status": "Check system health and resources",
            "Clean Logs": "Clean old log files",
            "Update Models": "Update ML models with new data",
            "Backup Data": "Backup trading data and configurations",
            "Reset System": "Reset system to default state"
        }
        
        print_menu("System Maintenance", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            check_system_status()
        elif choice == 2:
            clean_logs()
        elif choice == 3:
            run_command("python3 main.py --mode train", "Updating models...")
        elif choice == 4:
            backup_data()
        elif choice == 5:
            confirm_reset()
        
        input("\nPress Enter to continue...")

def help_menu():
    """Help and documentation menu"""
    while True:
        clear_screen()
        print_header()
        
        options = {
            "Quick Start Guide": "Show quick start instructions",
            "Command Reference": "Show all available commands",
            "Configuration Guide": "Show configuration options",
            "Troubleshooting": "Common issues and solutions",
            "About TradeX": "System information and version"
        }
        
        print_menu("Help & Documentation", options)
        choice = get_user_choice(len(options))
        
        if choice == 0:
            break
        elif choice == 1:
            show_quick_start()
        elif choice == 2:
            show_command_reference()
        elif choice == 3:
            show_configuration_guide()
        elif choice == 4:
            show_troubleshooting()
        elif choice == 5:
            show_about()
        
        input("\nPress Enter to continue...")

# Helper functions for menu actions
def check_system_status():
    """Check system status"""
    print("\n🔍 System Status Check")
    print("-" * 40)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual Environment: Active")
    else:
        print("❌ Virtual Environment: Not active")
    
    # Check key files
    key_files = ['main.py', 'config.py', 'trading_engine.py', 'requirements.txt']
    for file in key_files:
        if Path(file).exists():
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        print(f"💾 Disk Space: {free // (1024**3)} GB free")
    except:
        print("💾 Disk Space: Unable to check")

def check_configuration():
    """Check configuration"""
    print("\n⚙️ Configuration Check")
    print("-" * 40)
    
    try:
        from config import Config
        print(f"API Key: {'✅ Set' if Config.CB_API_KEY else '❌ Not set'}")
        print(f"API Secret: {'✅ Set' if Config.CB_API_SECRET else '❌ Not set'}")
        print(f"Passphrase: {'✅ Set' if Config.CB_API_PASSPHRASE else '❌ Not set'}")
        print(f"Trade Amount: ${Config.TRADE_AMOUNT_USD}")
        print(f"Supported Pairs: {', '.join(Config.SUPPORTED_PAIRS)}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

def confirm_live_trading():
    """Confirm live trading"""
    print("\n⚠️ WARNING: Live Trading")
    print("This will trade with REAL MONEY!")
    print("-" * 40)
    
    confirm1 = input("Are you sure you want to start live trading? (yes/NO): ").strip().lower()
    if confirm1 == 'yes':
        confirm2 = input("Type 'CONFIRM' to proceed: ").strip()
        if confirm2 == 'CONFIRM':
            run_command("python3 main.py --mode trade", "Starting live trading...")
        else:
            print("❌ Live trading cancelled")
    else:
        print("❌ Live trading cancelled")

def custom_backtest():
    """Custom backtest with user input"""
    print("\n📊 Custom Backtest")
    print("-" * 40)
    
    start_date = input("Start date (YYYY-MM-DD) [2024-01-01]: ").strip() or "2024-01-01"
    end_date = input("End date (YYYY-MM-DD) [2024-01-31]: ").strip() or "2024-01-31"
    balance = input("Initial balance [1000]: ").strip() or "1000"
    
    command = f"python3 main.py --mode backtest --start-date {start_date} --end-date {end_date} --initial-balance {balance}"
    run_command(command, "Running custom backtest...")

def custom_report_generation():
    """Custom report generation"""
    print("\n📄 Custom Report Generation")
    print("-" * 40)
    
    days = input("Days to analyze [30]: ").strip() or "30"
    output = input("Output filename [tradex_report.pdf]: ").strip() or "tradex_report.pdf"
    
    command = f"python3 main.py --mode report --days {days} --output {output}"
    run_command(command, "Generating custom report...")

def check_trading_status():
    """Check trading status"""
    print("\n📈 Trading Status")
    print("-" * 40)
    
    # Check if trading processes are running
    try:
        result = subprocess.run("ps aux | grep -E '(main.py|start_tradex.py)' | grep -v grep", shell=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ Trading processes running:")
            print(result.stdout)
        else:
            print("❌ No trading processes running")
    except:
        print("❌ Unable to check trading status")

def stop_trading():
    """Stop trading operations"""
    print("\n🛑 Stopping Trading Operations")
    print("-" * 40)
    
    try:
        subprocess.run("pkill -f 'main.py'", shell=True)
        subprocess.run("pkill -f 'start_tradex.py'", shell=True)
        print("✅ Trading operations stopped")
    except:
        print("❌ Unable to stop trading operations")

def show_quick_start():
    """Show quick start guide"""
    print("\n🚀 Quick Start Guide")
    print("=" * 50)
    print("1. Setup: Run 'Virtual Environment Setup'")
    print("2. Test: Run 'System Test' to verify everything works")
    print("3. Train: Run 'Train Models' to prepare ML models")
    print("4. Test: Run 'Paper Trading' to test with real data")
    print("5. Trade: Run 'Live Trading' when ready")
    print("\n💡 All commands are available in the menu system!")

def show_command_reference():
    """Show command reference"""
    print("\n📋 Command Reference")
    print("=" * 50)
    print("Setup:")
    print("  python3 setup_venv.py")
    print("  ./setup_jetson.sh")
    print("  ./fix_dependencies.sh")
    print("\nTesting:")
    print("  python3 test_system.py")
    print("  python3 main.py --mode backtest")
    print("\nTraining:")
    print("  python3 main.py --mode train")
    print("\nTrading:")
    print("  python3 main.py --mode paper")
    print("  python3 main.py --mode trade")
    print("  python3 start_tradex.py")
    print("\nReporting:")
    print("  python3 main.py --mode report")

def show_about():
    """Show about information"""
    print("\nℹ️ About TradeX")
    print("=" * 50)
    print("TradeX - Crypto Trading Automation Platform")
    print("Version: 2.0")
    print("Platform: 24/7 Automated Trading")
    print("Supported: BTC, ETH")
    print("Features: ML, Backtesting, Paper Trading, Live Trading")
    print("Deployment: Jetson Orin Nano")

# Placeholder functions for future implementation
def check_training_status():
    print("⚠️ Training status feature coming soon")

def show_training_config():
    print("⚠️ Training configuration feature coming soon")

def show_backtest_results():
    print("⚠️ Backtest results viewer coming soon")

def show_backtest_config():
    print("⚠️ Backtest configuration feature coming soon")

def show_performance_analytics():
    print("⚠️ Performance analytics feature coming soon")

def generate_system_report():
    print("⚠️ System report generation coming soon")

def analyze_logs():
    print("⚠️ Log analysis feature coming soon")

def export_data():
    print("⚠️ Data export feature coming soon")

def clean_logs():
    print("⚠️ Log cleaning feature coming soon")

def backup_data():
    print("⚠️ Data backup feature coming soon")

def confirm_reset():
    print("⚠️ System reset feature coming soon")

def show_configuration_guide():
    print("⚠️ Configuration guide coming soon")

def show_troubleshooting():
    print("⚠️ Troubleshooting guide coming soon")

def main():
    """Main menu function"""
    # Activate virtual environment
    if not activate_virtual_environment():
        print("❌ Virtual environment not available. Please run setup first.")
        sys.exit(1)
    
    while True:
        clear_screen()
        print_header()
        
        main_options = {
            "Setup & Installation": "Configure virtual environment and install dependencies",
            "Testing & Validation": "Test system components and verify functionality",
            "Machine Learning Training": "Train and update ML models",
            "Trading Operations": "Start and manage trading operations",
            "Backtesting": "Test strategies with historical data",
            "Reporting & Analytics": "Generate reports and analyze performance",
            "System Maintenance": "Maintain and manage the system",
            "Help & Documentation": "Get help and view documentation"
        }
        
        print_menu("Main Menu", main_options)
        choice = get_user_choice(len(main_options))
        
        if choice == 0:
            print("\n👋 Thank you for using TradeX!")
            break
        elif choice == 1:
            setup_menu()
        elif choice == 2:
            testing_menu()
        elif choice == 3:
            training_menu()
        elif choice == 4:
            trading_menu()
        elif choice == 5:
            backtesting_menu()
        elif choice == 6:
            reporting_menu()
        elif choice == 7:
            maintenance_menu()
        elif choice == 8:
            help_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 TradeX menu interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
