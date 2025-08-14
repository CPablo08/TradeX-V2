const express = require('express');
const router = express.Router();
const fs = require('fs').promises;
const path = require('path');

// Get system status
router.get('/status', async (req, res) => {
  try {
    const uptime = process.uptime();
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    const status = {
      uptime: Math.floor(uptime),
      memory: {
        used: Math.round(memoryUsage.heapUsed / 1024 / 1024),
        total: Math.round(memoryUsage.heapTotal / 1024 / 1024),
        external: Math.round(memoryUsage.external / 1024 / 1024)
      },
      cpu: {
        user: Math.round(cpuUsage.user / 1000),
        system: Math.round(cpuUsage.system / 1000)
      },
      timestamp: new Date().toISOString()
    };
    
    res.json({ success: true, data: status });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get trading status
router.get('/trading-status', async (req, res) => {
  try {
    const getTradingStatus = req.app.locals.getTradingStatus;
    if (!getTradingStatus) {
      return res.status(500).json({ success: false, error: 'Trading system not initialized' });
    }
    
    const status = getTradingStatus();
    res.json({
      success: true,
      data: {
        isActive: status.isActive,
        tradingMode: status.mode,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start trading
router.post('/start-trading', async (req, res) => {
  try {
    const startTrading = req.app.locals.startTrading;
    if (!startTrading) {
      return res.status(500).json({ success: false, error: 'Trading system not initialized' });
    }
    
    const result = startTrading();
    res.json({ success: result.success, message: result.message, timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Stop trading
router.post('/stop-trading', async (req, res) => {
  try {
    const stopTrading = req.app.locals.stopTrading;
    if (!stopTrading) {
      return res.status(500).json({ success: false, error: 'Trading system not initialized' });
    }
    
    const result = stopTrading();
    res.json({ success: result.success, message: result.message, timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Change trading mode
router.post('/trading-mode', async (req, res) => {
  try {
    const { mode } = req.body;
    if (!mode || !['paper', 'real'].includes(mode)) {
      return res.status(400).json({ success: false, error: 'Invalid trading mode. Must be "paper" or "real"' });
    }
    
    process.env.TRADING_MODE = mode;
    console.log(`Trading mode changed to: ${mode}`);
    res.json({ success: true, message: `Trading mode changed to ${mode}`, timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get trading logs
router.get('/trading-logs', async (req, res) => {
  try {
    const logPath = path.join(__dirname, '../../logs/tradex.log');
    const logContent = await fs.readFile(logPath, 'utf8');
    
    const lines = logContent.split('\n').filter(line => line.trim());
    const recentLogs = lines.slice(-50).map(line => {
      try {
        const match = line.match(/\[(.*?)\] \[(.*?)\] (.*)/);
        if (match) {
          return {
            timestamp: match[1],
            level: match[2],
            message: match[3]
          };
        }
        return {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: line
        };
      } catch (error) {
        return {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: line
        };
      }
    });
    
    res.json({ success: true, data: recentLogs });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get errors
router.get('/errors', async (req, res) => {
  try {
    const logPath = path.join(__dirname, '../../logs/tradex.log');
    const logContent = await fs.readFile(logPath, 'utf8');
    
    const lines = logContent.split('\n').filter(line => line.trim());
    const errorLogs = lines
      .filter(line => line.includes('[ERROR]') || line.includes('[WARN]'))
      .slice(-20)
      .map(line => {
        try {
          const match = line.match(/\[(.*?)\] \[(.*?)\] (.*)/);
          if (match) {
            return {
              timestamp: match[1],
              level: match[2],
              message: match[3]
            };
          }
          return {
            timestamp: new Date().toISOString(),
            level: 'error',
            message: line
          };
        } catch (error) {
          return {
            timestamp: new Date().toISOString(),
            level: 'error',
            message: line
          };
        }
      });
    
    res.json({ success: true, data: errorLogs });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Restart trading session
router.post('/restart-session', async (req, res) => {
  try {
    const db = req.app.locals.db;
    await db.run('DELETE FROM trade_history');
    await db.run('DELETE FROM performance_metrics');
    await db.run('DELETE FROM account_data');
    console.log('Trading session restarted - all data cleared');
    res.json({ success: true, message: 'Trading session restarted successfully', timestamp: new Date().toISOString() });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Update strategy
router.post('/update-strategy', async (req, res) => {
  try {
    const { symbol, code } = req.body;
    
    if (!symbol || !code) {
      return res.status(400).json({ success: false, error: 'Symbol and code are required' });
    }
    
    if (!['BTC', 'ETH'].includes(symbol)) {
      return res.status(400).json({ success: false, error: 'Symbol must be BTC or ETH' });
    }
    
    const logicEngine = req.app.locals.logicEngine;
    
    // Validate the Pine Script code
    const validation = logicEngine.validatePineScript(code);
    if (!validation.valid) {
      return res.status(400).json({ success: false, error: validation.error });
    }
    
    // Update the strategy
    await logicEngine.updateStrategy(symbol, `${symbol} Strategy`, code);
    
    res.json({ 
      success: true, 
      message: `${symbol} strategy updated successfully`, 
      timestamp: new Date().toISOString() 
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
