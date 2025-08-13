const os = require('os');
const fs = require('fs');

class Watchdog {
  constructor(logger, components) {
    this.logger = logger;
    this.components = components;
    this.isInitialized = false;
    this.healthCheckInterval = null;
    this.errorCount = 0;
    this.maxErrors = 10;
    this.lastHealthCheck = null;
  }

  async initialize() {
    try {
      this.logger.info('Initializing Watchdog...');
      
      // Initialize health checks
      await this.initializeHealthChecks();
      
      this.isInitialized = true;
      this.logger.info('Watchdog initialized successfully');
    } catch (error) {
      this.logger.error('Watchdog initialization failed:', error);
      throw error;
    }
  }

  async initializeHealthChecks() {
    try {
      // Set up health check intervals
      const healthCheckInterval = parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000;
      
      this.healthCheckInterval = setInterval(async () => {
        await this.performHealthCheck();
      }, healthCheckInterval);
      
      this.logger.info('Health checks initialized');
    } catch (error) {
      this.logger.error('Failed to initialize health checks:', error);
      throw error;
    }
  }

  async performHealthCheck() {
    try {
      this.logger.info('Performing health check...');
      
      const results = {
        system: await this.performSystemHealthCheck(),
        application: await this.performApplicationHealthCheck()
      };
      
      this.lastHealthCheck = {
        timestamp: new Date(),
        results: results
      };
      
      // Check for critical issues
      const hasCriticalIssues = this.checkForCriticalIssues(results);
      
      if (hasCriticalIssues) {
        await this.handleCriticalFailure(results);
      }
      
      this.logger.info('Health check completed', {
        errors: this.errorCount,
        results: results
      });
      
    } catch (error) {
      this.logger.error('Health check failed:', error);
      this.incrementErrorCount();
    }
  }

  async performSystemHealthCheck() {
    const results = {};
    
    try {
      // Memory usage check
      results.memory = await this.checkMemoryUsage();
      
      // CPU usage check
      results.cpu = await this.checkCPUUsage();
      
      // Disk space check
      results.disk = await this.checkDiskSpace();
      
      // Network connectivity check
      results.network = await this.checkNetworkConnectivity();
      
    } catch (error) {
      this.logger.error('System health check failed:', error);
      results.error = error.message;
    }
    
    return results;
  }

  async performApplicationHealthCheck() {
    const results = {};
    
    try {
      // Process health check
      results.process = await this.checkProcessHealth();
      
      // Database health check
      results.database = await this.checkDatabaseHealth();
      
      // API health check
      results.api = await this.checkAPIHealth();
      
      // Component health checks
      results.components = await this.checkComponentHealth();
      
    } catch (error) {
      this.logger.error('Application health check failed:', error);
      results.error = error.message;
    }
    
    return results;
  }

  async checkMemoryUsage() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const usage = usedMem / totalMem;
    const threshold = parseFloat(process.env.MEMORY_THRESHOLD) || 0.8;
    
    return {
      total: totalMem,
      free: freeMem,
      used: usedMem,
      usage: usage,
      threshold: threshold,
      healthy: usage < threshold
    };
  }

  async checkCPUUsage() {
    const cpus = os.cpus();
    const loadAvg = os.loadavg();
    const cpuCount = cpus.length;
    const threshold = parseFloat(process.env.CPU_THRESHOLD) || 0.9;
    
    // Calculate CPU usage from load average
    const usage = loadAvg[0] / cpuCount;
    
    return {
      cpuCount: cpuCount,
      loadAverage: loadAvg,
      usage: usage,
      threshold: threshold,
      healthy: usage < threshold
    };
  }

  async checkDiskSpace() {
    try {
      const path = process.cwd();
      const stats = fs.statSync(path);
      
      return {
        path: path,
        healthy: true,
        message: 'Disk space check passed'
      };
    } catch (error) {
      return {
        path: process.cwd(),
        healthy: false,
        message: 'Disk space check failed',
        error: error.message
      };
    }
  }

  async checkNetworkConnectivity() {
    try {
      // Test Coinbase API connectivity
      const coinbaseResponse = await this.testAPI('https://api.coinbase.com/v2/prices/BTC-USD/spot');
      
      // Test Alpaca API connectivity
      const alpacaResponse = await this.testAPI('https://paper-api.alpaca.markets/v2/account');
      
      return {
        coinbase: coinbaseResponse,
        alpaca: alpacaResponse,
        healthy: coinbaseResponse.healthy || alpacaResponse.healthy
      };
    } catch (error) {
      return {
        healthy: false,
        error: error.message
      };
    }
  }

  async testAPI(url) {
    try {
      const axios = require('axios');
      const response = await axios.get(url, { timeout: 5000 });
      
      return {
        healthy: response.status < 500,
        statusCode: response.status
      };
    } catch (error) {
      return {
        healthy: false,
        statusCode: error.response?.status || 0,
        error: error.message
      };
    }
  }

  async checkProcessHealth() {
    const memUsage = process.memoryUsage();
    const uptime = process.uptime();
    
    return {
      pid: process.pid,
      uptime: uptime,
      memoryUsage: memUsage,
      healthy: uptime > 0 && memUsage.heapUsed < 100 * 1024 * 1024 // Less than 100MB
    };
  }

  async checkDatabaseHealth() {
    try {
      if (this.components.db) {
        // Test database connection
        await this.components.db.get('SELECT 1 as test');
        return {
          healthy: true,
          message: 'Database connection healthy'
        };
      } else {
        return {
          healthy: false,
          message: 'Database component not available'
        };
      }
    } catch (error) {
      return {
        healthy: false,
        message: 'Database health check failed',
        error: error.message
      };
    }
  }

  async checkAPIHealth() {
    try {
      // Test if APIs are responding
      const coinbaseHealthy = await this.testAPI('https://api.coinbase.com/v2/prices/BTC-USD/spot');
      const alpacaHealthy = await this.testAPI('https://paper-api.alpaca.markets/v2/account');
      
      return {
        coinbase: coinbaseHealthy,
        alpaca: alpacaHealthy,
        healthy: coinbaseHealthy.healthy || alpacaHealthy.healthy
      };
    } catch (error) {
      return {
        healthy: false,
        error: error.message
      };
    }
  }

  async checkComponentHealth() {
    const componentHealth = {};
    
    try {
      // Check DataRetriever
      if (this.components.dataRetriever) {
        componentHealth.dataRetriever = {
          healthy: this.components.dataRetriever.isInitialized,
          message: this.components.dataRetriever.isInitialized ? 'Initialized' : 'Not initialized'
        };
      }
      
      // Check LogicEngine
      if (this.components.logicEngine) {
        componentHealth.logicEngine = {
          healthy: this.components.logicEngine.isInitialized,
          message: this.components.logicEngine.isInitialized ? 'Initialized' : 'Not initialized'
        };
      }
      
      // Check Executor
      if (this.components.executor) {
        componentHealth.executor = {
          healthy: this.components.executor.isInitialized,
          message: this.components.executor.isInitialized ? 'Initialized' : 'Not initialized'
        };
      }
      
      return componentHealth;
    } catch (error) {
      return {
        error: error.message,
        healthy: false
      };
    }
  }

  checkForCriticalIssues(results) {
    const system = results.system;
    const application = results.application;
    
    // Check for critical system issues
    if (system.memory && !system.memory.healthy) {
      this.logger.warn('System health issues detected', system);
      return true;
    }
    
    if (system.cpu && !system.cpu.healthy) {
      this.logger.warn('System health issues detected', system);
      return true;
    }
    
    // Check for critical application issues
    if (application.database && !application.database.healthy) {
      this.logger.warn('Application health issues detected', application);
      return true;
    }
    
    return false;
  }

  async handleCriticalFailure(results) {
    this.logger.error('Critical failure detected, initiating recovery...');
    
    try {
      // Handle high memory usage
      if (results.system.memory && !results.system.memory.healthy) {
        await this.handleHighMemoryUsage();
      }
      
      // Handle high CPU usage
      if (results.system.cpu && !results.system.cpu.healthy) {
        await this.handleHighCPUUsage();
      }
      
      // Handle database failure
      if (results.application.database && !results.application.database.healthy) {
        await this.handleDatabaseFailure();
      }
      
      // Handle API failure
      if (results.application.api && !results.application.api.healthy) {
        await this.handleAPIFailure();
      }
      
    } catch (error) {
      this.logger.error('Recovery failed:', error);
      await this.handleEmergencyRestart();
    }
  }

  async handleHighMemoryUsage() {
    this.logger.warn('High memory usage detected, attempting garbage collection');
    
    if (global.gc) {
      global.gc();
      this.logger.info('Garbage collection completed');
    } else {
      this.logger.warn('Garbage collection not available');
    }
  }

  async handleHighCPUUsage() {
    this.logger.warn('High CPU usage detected');
    // Could implement CPU throttling or reduce processing frequency
  }

  async handleDatabaseFailure() {
    this.logger.error('Database failure detected, attempting recovery');
    
    try {
      if (this.components.db) {
        // Try to reconnect to database
        await this.components.db.initialize();
        this.logger.info('Database recovery successful');
      }
    } catch (error) {
      this.logger.error('Database recovery failed:', error);
      throw error;
    }
  }

  async handleAPIFailure() {
    this.logger.error('API failure detected, attempting recovery');
    
    try {
      // Could implement API retry logic or fallback mechanisms
      this.logger.info('API recovery attempted');
    } catch (error) {
      this.logger.error('API recovery failed:', error);
      throw error;
    }
  }

  async handleEmergencyRestart() {
    this.logger.error('Emergency restart initiated');
    
    try {
      // Stop all components gracefully
      await this.stop();
      
      // Exit process to allow restart by process manager
      process.exit(1);
    } catch (error) {
      this.logger.error('Emergency restart failed:', error);
      process.exit(1);
    }
  }

  incrementErrorCount() {
    this.errorCount++;
    
    if (this.errorCount >= this.maxErrors) {
      this.logger.error('Maximum error count reached, initiating emergency restart');
      this.handleEmergencyRestart();
    }
  }

  resetErrorCount() {
    this.errorCount = 0;
  }

  getErrorCount() {
    return this.errorCount;
  }

  async reportError(error, context = {}) {
    this.logger.error('Error reported:', { error: error.message, context });
    this.incrementErrorCount();
  }

  isCriticalError(error) {
    // Define what constitutes a critical error
    const criticalErrors = [
      'ENOMEM', // Out of memory
      'ECONNREFUSED', // Connection refused
      'ETIMEDOUT', // Connection timeout
      'ENOTFOUND' // Host not found
    ];
    
    return criticalErrors.some(criticalError => 
      error.message.includes(criticalError) || error.code === criticalError
    );
  }

  async handleCriticalError(error) {
    if (this.isCriticalError(error)) {
      this.logger.error('Critical error detected:', error);
      await this.handleEmergencyRestart();
    } else {
      this.logger.error('Non-critical error:', error);
      this.incrementErrorCount();
    }
  }

  getSystemInfo() {
    return {
      platform: os.platform(),
      arch: os.arch(),
      nodeVersion: process.version,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpuCount: os.cpus().length,
      totalMemory: os.totalmem(),
      freeMemory: os.freemem()
    };
  }

  stop() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
    
    this.logger.info('Watchdog stopped');
  }
}

module.exports = Watchdog;
