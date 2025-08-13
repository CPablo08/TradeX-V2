const express = require('express');
const router = express.Router();
const fs = require('fs').promises;
const path = require('path');

// Get trading logs specifically
router.get('/trading-logs', async (req, res) => {
  try {
    const logPath = path.join(__dirname, '../../logs/tradex.log');
    
    try {
      const logContent = await fs.readFile(logPath, 'utf8');
      const lines = logContent.trim().split('\n').filter(line => line.trim());
      
      // Parse JSON log entries and filter for trading-related logs only
      const tradingLogs = lines
        .map(line => {
          try {
            return JSON.parse(line);
          } catch (e) {
            return null;
          }
        })
        .filter(entry => entry && entry.message && (
          entry.message.includes('Trading decision') ||
          entry.message.includes('Executing trade') ||
          entry.message.includes('Paper trade executed') ||
          entry.message.includes('Trade logged') ||
          entry.message.includes('Market data fetched')
        ))
        .map(entry => ({
          timestamp: entry.timestamp,
          level: entry.level,
          service: entry.service || 'system',
          message: entry.message,
          details: entry.details || null
        }))
        .slice(-50); // Get last 50 trading logs
      
      res.json(tradingLogs);
    } catch (fileError) {
      // If log file doesn't exist, return empty array
      res.json([]);
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get system errors and logs
router.get('/errors', async (req, res) => {
  try {
    const logPath = path.join(__dirname, '../../logs/tradex.log');
    
    try {
      const logContent = await fs.readFile(logPath, 'utf8');
      const lines = logContent.trim().split('\n').filter(line => line.trim());
      
      // Parse JSON log entries and filter for trading-related logs
      const errors = lines
        .map(line => {
          try {
            return JSON.parse(line);
          } catch (e) {
            return null;
          }
        })
        .filter(entry => entry && (
          entry.level === 'error' || 
          entry.level === 'warn' || 
          (entry.message && (
            entry.message.includes('Trading decision') ||
            entry.message.includes('Executing trade') ||
            entry.message.includes('Paper trade executed') ||
            entry.message.includes('Trade logged') ||
            entry.message.includes('Market data fetched')
          ))
        ))
        .map(entry => ({
          timestamp: entry.timestamp,
          level: entry.level,
          service: entry.service || 'system',
          message: entry.message,
          details: entry.details || null
        }))
        .slice(-50); // Get last 50 entries
      
      res.json(errors);
    } catch (fileError) {
      // If log file doesn't exist, return empty array
      res.json([]);
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get system status
router.get('/status', async (req, res) => {
  try {
    const status = {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
      timestamp: new Date().toISOString(),
      version: process.version,
      platform: process.platform,
      tradingMode: process.env.TRADING_MODE || 'paper'
    };
    
    res.json(status);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Update trading mode
router.post('/trading-mode', async (req, res) => {
  try {
    const { mode } = req.body;
    
    if (mode !== 'paper' && mode !== 'real') {
      return res.status(400).json({
        success: false,
        error: 'Invalid trading mode. Must be "paper" or "real"'
      });
    }

    // Update environment variable
    process.env.TRADING_MODE = mode;
    
    // Log the change
    console.log(`Trading mode changed to: ${mode}`);
    
    res.json({
      success: true,
      message: `Trading mode updated to ${mode}`,
      mode: mode
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start/Stop trading
router.post('/start-trading', async (req, res) => {
  try {
    const { action, mode } = req.body;
    
    if (action !== 'start' && action !== 'stop') {
      return res.status(400).json({
        success: false,
        error: 'Invalid action. Must be "start" or "stop"'
      });
    }

    if (action === 'start') {
      // Update trading mode if provided
      if (mode) {
        process.env.TRADING_MODE = mode;
      }
      
      // Start trading system
      const result = req.app.locals.startTrading();
      
      res.json({
        success: result.success,
        message: result.message,
        action: 'start',
        mode: process.env.TRADING_MODE || 'paper'
      });
    } else {
      // Stop trading system
      const result = req.app.locals.stopTrading();
      
      res.json({
        success: result.success,
        message: result.message,
        action: 'stop'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get trading status
router.get('/trading-status', async (req, res) => {
  try {
    const status = req.app.locals.getTradingStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Restart trading session
router.post('/restart-session', async (req, res) => {
  try {
    const db = req.app.locals.db;
    
    // Clear trade history
    await db.run('DELETE FROM trade_history');
    
    // Reset performance metrics
    await db.run('DELETE FROM performance_metrics');
    
    // Reset account data
    await db.run('DELETE FROM account_data');
    
    // Log the restart
    console.log('Trading session restarted - all data cleared');
    
    res.json({
      success: true,
      message: 'Trading session restarted successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
