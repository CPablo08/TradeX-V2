#!/usr/bin/env python3
"""
TradeX System Monitor
Monitors the trading system and restarts if needed for 24/7 operation
"""

import os
import sys
import time
import json
import subprocess
import psutil
import requests
from datetime import datetime, timedelta
from loguru import logger
import schedule

class TradeXMonitor:
    def __init__(self):
        self.process_name = "python"
        self.script_name = "main.py"
        self.max_restart_attempts = 5
        self.restart_attempts = 0
        self.last_restart = None
        self.monitor_start = datetime.now()
        
        # Setup logging
        logger.add("monitor.log", rotation="1 day", retention="7 days")
        
    def find_tradex_process(self):
        """Find the TradeX trading process"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if (proc.info['name'] == self.process_name and 
                    proc.info['cmdline'] and 
                    self.script_name in ' '.join(proc.info['cmdline'])):
                    return proc
            return None
        except Exception as e:
            logger.error(f"Error finding TradeX process: {e}")
            return None
    
    def check_process_health(self):
        """Check if the trading process is healthy"""
        try:
            proc = self.find_tradex_process()
            if not proc:
                logger.warning("TradeX process not found")
                return False
            
            # Check if process is responsive
            if proc.status() == psutil.STATUS_ZOMBIE:
                logger.error("TradeX process is zombie")
                return False
            
            # Check memory usage
            memory_info = proc.memory_info()
            memory_percent = proc.memory_percent()
            
            if memory_percent > 90:
                logger.warning(f"High memory usage: {memory_percent:.1f}%")
            
            # Check CPU usage
            cpu_percent = proc.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            
            logger.info(f"TradeX process healthy - PID: {proc.pid}, Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"Error checking process health: {e}")
            return False
    
    def check_system_resources(self):
        """Check overall system resources"""
        try:
            # Memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"System memory usage high: {memory.percent:.1f}%")
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                logger.warning(f"System CPU usage high: {cpu_percent:.1f}%")
            
            # Disk
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                logger.warning(f"System disk usage high: {disk.percent:.1f}%")
            
            # Network
            try:
                response = requests.get(Config.BINANCE_BASE_URL, timeout=5)
                if response.status_code != 200:
                    logger.warning("Network connectivity issues")
            except Exception as e:
                logger.warning(f"Network connectivity check failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return False
    
    def check_log_file(self):
        """Check recent log entries for errors"""
        try:
            log_file = "tradex.log"
            if not os.path.exists(log_file):
                return True
            
            # Check last 100 lines for critical errors
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                
                for line in recent_lines:
                    if any(error in line.lower() for error in ['critical', 'emergency', 'fatal']):
                        logger.warning(f"Critical error found in logs: {line.strip()}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking log file: {e}")
            return True
    
    def restart_tradex(self):
        """Restart the TradeX trading system"""
        try:
            logger.info("Attempting to restart TradeX...")
            
            # Kill existing process
            proc = self.find_tradex_process()
            if proc:
                logger.info(f"Terminating existing process (PID: {proc.pid})")
                proc.terminate()
                proc.wait(timeout=30)
            
            # Start new process
            logger.info("Starting new TradeX process...")
            subprocess.Popen([
                sys.executable, "main.py", "--mode", "trade"
            ], cwd=os.getcwd())
            
            self.restart_attempts += 1
            self.last_restart = datetime.now()
            
            # Wait for process to start
            time.sleep(10)
            
            # Verify process started
            if self.find_tradex_process():
                logger.info("TradeX restarted successfully")
                return True
            else:
                logger.error("Failed to restart TradeX")
                return False
                
        except Exception as e:
            logger.error(f"Error restarting TradeX: {e}")
            return False
    
    def check_system_state(self):
        """Check if system state file is recent"""
        try:
            state_file = "system_state.json"
            if not os.path.exists(state_file):
                return True
            
            # Check if state file is recent (within last hour)
            file_time = datetime.fromtimestamp(os.path.getmtime(state_file))
            if datetime.now() - file_time > timedelta(hours=1):
                logger.warning("System state file is old - possible system freeze")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking system state: {e}")
            return True
    
    def monitor_cycle(self):
        """Execute one monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle...")
            
            # Check if process exists and is healthy
            if not self.check_process_health():
                logger.warning("TradeX process health check failed")
                
                # Check if we should restart
                if (self.restart_attempts < self.max_restart_attempts and
                    (self.last_restart is None or 
                     datetime.now() - self.last_restart > timedelta(minutes=5))):
                    
                    if self.restart_tradex():
                        logger.info("Process restarted successfully")
                    else:
                        logger.error("Failed to restart process")
                else:
                    logger.error("Maximum restart attempts reached or too soon to restart")
            
            # Check system resources
            self.check_system_resources()
            
            # Check log file for errors
            if not self.check_log_file():
                logger.warning("Critical errors found in logs")
            
            # Check system state
            if not self.check_system_state():
                logger.warning("System state check failed")
            
            logger.info("Monitoring cycle completed")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def log_monitor_status(self):
        """Log comprehensive monitor status"""
        try:
            uptime = datetime.now() - self.monitor_start
            proc = self.find_tradex_process()
            
            logger.info("=" * 60)
            logger.info("MONITOR STATUS REPORT")
            logger.info("=" * 60)
            logger.info(f"Monitor Uptime: {uptime}")
            logger.info(f"TradeX Process: {'Running' if proc else 'Not Found'}")
            if proc:
                logger.info(f"TradeX PID: {proc.pid}")
                logger.info(f"TradeX Memory: {proc.memory_percent():.1f}%")
                logger.info(f"TradeX CPU: {proc.cpu_percent():.1f}%")
            logger.info(f"Restart Attempts: {self.restart_attempts}/{self.max_restart_attempts}")
            logger.info(f"Last Restart: {self.last_restart}")
            
            # System resources
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            logger.info(f"System Memory: {memory.percent:.1f}%")
            logger.info(f"System CPU: {cpu:.1f}%")
            logger.info(f"System Disk: {disk.percent:.1f}%")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error logging monitor status: {e}")
    
    def run(self):
        """Run the monitor continuously"""
        logger.info("Starting TradeX System Monitor...")
        
        # Schedule monitoring tasks
        schedule.every(2).minutes.do(self.monitor_cycle)  # Check every 2 minutes
        schedule.every(6).hours.do(self.log_monitor_status)  # Status report every 6 hours
        
        # Initial monitoring cycle
        self.monitor_cycle()
        
        # Main monitoring loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitor main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = TradeXMonitor()
    monitor.run()
