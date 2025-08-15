#!/usr/bin/env python3
"""
TradeX Startup Script
Single command to start the entire trading system with automatic monitoring
"""

import os
import sys
import time
import subprocess
import threading
import signal
import psutil
import requests
from datetime import datetime, timedelta
from loguru import logger
import json

class TradeXLauncher:
    def __init__(self):
        self.trading_process = None
        self.monitor_process = None
        self.status_thread = None
        self.running = True
        self.start_time = datetime.now()
        
        # Setup logging
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            "tradex_launcher.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="1 day",
            retention="7 days"
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}. Shutting down TradeX...")
        self.shutdown()
        sys.exit(0)
    
    def check_environment(self):
        """Check if environment is properly configured"""
        logger.info("Checking environment...")
        
        # Check if .env file exists
        if not os.path.exists('.env'):
            logger.error("❌ .env file not found. Please create it from env_example.txt")
            return False
        
        # Check if models directory exists
        if not os.path.exists('models/'):
            logger.warning("⚠️  Models directory not found. You may need to train models first.")
        
        # Check if required files exist
        required_files = ['main.py', 'trading_engine.py', 'config.py']
        for file in required_files:
            if not os.path.exists(file):
                logger.error(f"❌ Required file not found: {file}")
                return False
        
        logger.info("✅ Environment check passed")
        return True
    
    def start_trading_system(self):
        """Start the main trading system"""
        try:
            logger.info("🚀 Starting TradeX Trading System...")
            
            # Start the trading system
            self.trading_process = subprocess.Popen([
                sys.executable, "main.py", "--mode", "trade"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment to see if it starts successfully
            time.sleep(3)
            
            if self.trading_process.poll() is None:
                logger.info(f"✅ Trading system started (PID: {self.trading_process.pid})")
                return True
            else:
                stdout, stderr = self.trading_process.communicate()
                logger.error(f"❌ Trading system failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting trading system: {e}")
            return False
    
    def start_monitor(self):
        """Start the external monitor"""
        try:
            logger.info("🔍 Starting TradeX Monitor...")
            
            # Start the monitor
            self.monitor_process = subprocess.Popen([
                sys.executable, "monitor.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment to see if it starts successfully
            time.sleep(2)
            
            if self.monitor_process.poll() is None:
                logger.info(f"✅ Monitor started (PID: {self.monitor_process.pid})")
                return True
            else:
                stdout, stderr = self.monitor_process.communicate()
                logger.error(f"❌ Monitor failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting monitor: {e}")
            return False
    
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'trading_process': {
                    'running': False,
                    'pid': None,
                    'memory': 0,
                    'cpu': 0
                },
                'monitor_process': {
                    'running': False,
                    'pid': None,
                    'memory': 0,
                    'cpu': 0
                },
                'system_resources': {
                    'memory_percent': 0,
                    'cpu_percent': 0,
                    'disk_percent': 0
                },
                'network_status': False,
                'api_status': False,
                'trading_status': 'unknown'
            }
            
            # Check trading process
            if self.trading_process and self.trading_process.poll() is None:
                try:
                    proc = psutil.Process(self.trading_process.pid)
                    status['trading_process']['running'] = True
                    status['trading_process']['pid'] = self.trading_process.pid
                    status['trading_process']['memory'] = proc.memory_percent()
                    status['trading_process']['cpu'] = proc.cpu_percent()
                except:
                    pass
            
            # Check monitor process
            if self.monitor_process and self.monitor_process.poll() is None:
                try:
                    proc = psutil.Process(self.monitor_process.pid)
                    status['monitor_process']['running'] = True
                    status['monitor_process']['pid'] = self.monitor_process.pid
                    status['monitor_process']['memory'] = proc.memory_percent()
                    status['monitor_process']['cpu'] = proc.cpu_percent()
                except:
                    pass
            
            # System resources
            memory = psutil.virtual_memory()
            status['system_resources']['memory_percent'] = memory.percent
            status['system_resources']['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            
            disk = psutil.disk_usage('/')
            status['system_resources']['disk_percent'] = disk.percent
            
            # Network status
            try:
                response = requests.get('https://api.coinbase.com', timeout=5)
                status['network_status'] = response.status_code == 200
            except:
                status['network_status'] = False
            
            # API status (simplified check)
            status['api_status'] = status['network_status']
            
            # Trading status from log file
            if os.path.exists('tradex.log'):
                try:
                    with open('tradex.log', 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1]
                            if 'Trading signal' in last_line:
                                status['trading_status'] = 'active'
                            elif 'trading cycle' in last_line:
                                status['trading_status'] = 'running'
                            elif 'error' in last_line.lower():
                                status['trading_status'] = 'error'
                except:
                    pass
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return None
    
    def print_status(self, status):
        """Print formatted status to console"""
        try:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Print header
            print("=" * 80)
            print("🔄 TRADEX SYSTEM STATUS")
            print("=" * 80)
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Uptime: {status['uptime']}")
            print()
            
            # Trading Process Status
            trading = status['trading_process']
            if trading['running']:
                print(f"✅ Trading System: RUNNING (PID: {trading['pid']})")
                print(f"   📊 Memory: {trading['memory']:.1f}% | CPU: {trading['cpu']:.1f}%")
            else:
                print("❌ Trading System: STOPPED")
            
            # Monitor Process Status
            monitor = status['monitor_process']
            if monitor['running']:
                print(f"✅ Monitor: RUNNING (PID: {monitor['pid']})")
                print(f"   📊 Memory: {monitor['memory']:.1f}% | CPU: {monitor['cpu']:.1f}%")
            else:
                print("❌ Monitor: STOPPED")
            
            print()
            
            # System Resources
            resources = status['system_resources']
            print("💻 SYSTEM RESOURCES:")
            print(f"   🧠 Memory: {resources['memory_percent']:.1f}%")
            print(f"   🔥 CPU: {resources['cpu_percent']:.1f}%")
            print(f"   💾 Disk: {resources['disk_percent']:.1f}%")
            
            # Network Status
            print()
            print("🌐 NETWORK STATUS:")
            if status['network_status']:
                print("   ✅ Network: CONNECTED")
            else:
                print("   ❌ Network: DISCONNECTED")
            
            if status['api_status']:
                print("   ✅ Coinbase API: CONNECTED")
            else:
                print("   ❌ Coinbase API: DISCONNECTED")
            
            # Trading Status
            print()
            print("📈 TRADING STATUS:")
            trading_status = status['trading_status']
            if trading_status == 'active':
                print("   🟢 Trading: ACTIVE (Signals detected)")
            elif trading_status == 'running':
                print("   🟡 Trading: RUNNING (Monitoring markets)")
            elif trading_status == 'error':
                print("   🔴 Trading: ERROR (Check logs)")
            else:
                print("   ⚪ Trading: UNKNOWN")
            
            # Quick Actions
            print()
            print("🔧 QUICK ACTIONS:")
            print("   Press Ctrl+C to stop TradeX")
            print("   Check logs: tail -f tradex.log")
            print("   Check state: cat system_state.json")
            
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"Error printing status: {e}")
    
    def status_monitor_thread(self):
        """Thread for continuous status monitoring"""
        while self.running:
            try:
                status = self.get_system_status()
                if status:
                    self.print_status(status)
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                logger.error(f"Error in status monitor thread: {e}")
                time.sleep(5)
    
    def check_processes(self):
        """Check if processes are still running"""
        try:
            # Check trading process
            if self.trading_process and self.trading_process.poll() is not None:
                logger.warning("⚠️  Trading process stopped unexpectedly")
                return False
            
            # Check monitor process
            if self.monitor_process and self.monitor_process.poll() is not None:
                logger.warning("⚠️  Monitor process stopped unexpectedly")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking processes: {e}")
            return False
    
    def shutdown(self):
        """Graceful shutdown of all processes"""
        logger.info("🛑 Shutting down TradeX...")
        self.running = False
        
        try:
            # Stop trading process
            if self.trading_process and self.trading_process.poll() is None:
                logger.info("Stopping trading process...")
                self.trading_process.terminate()
                self.trading_process.wait(timeout=10)
            
            # Stop monitor process
            if self.monitor_process and self.monitor_process.poll() is None:
                logger.info("Stopping monitor process...")
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=10)
            
            logger.info("✅ TradeX shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def run(self):
        """Main launcher function"""
        logger.info("🚀 TradeX Launcher Starting...")
        
        # Check environment
        if not self.check_environment():
            logger.error("❌ Environment check failed. Exiting.")
            return
        
        # Start trading system
        if not self.start_trading_system():
            logger.error("❌ Failed to start trading system. Exiting.")
            return
        
        # Start monitor
        if not self.start_monitor():
            logger.warning("⚠️  Failed to start monitor. Continuing without external monitoring.")
        
        # Start status monitoring thread
        logger.info("📊 Starting status monitor (updates every 2 seconds)...")
        self.status_thread = threading.Thread(target=self.status_monitor_thread, daemon=True)
        self.status_thread.start()
        
        # Main loop
        logger.info("✅ TradeX is now running! Press Ctrl+C to stop.")
        try:
            while self.running:
                # Check if processes are still running
                if not self.check_processes():
                    logger.warning("⚠️  One or more processes stopped. Consider restarting.")
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.shutdown()

def main():
    """Main entry point"""
    launcher = TradeXLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
