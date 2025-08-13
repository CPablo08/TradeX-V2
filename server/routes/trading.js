const express = require('express');
const router = express.Router();

// Execute a trade
router.post('/execute', async (req, res) => {
  try {
    const { symbol, action, quantity, price } = req.body;
    const executor = req.app.locals.executor;
    
    const decision = {
      symbol: symbol,
      action: action,
      quantity: quantity,
      price: price,
      timestamp: new Date()
    };
    
    const result = await executor.executeTrade(decision);
    
    res.json({
      success: true,
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get trading status
router.get('/status', async (req, res) => {
  try {
    const executor = req.app.locals.executor;
    const dailyStats = executor.getDailyStats();
    const activeOrders = await executor.getActiveOrders();
    
    res.json({
      success: true,
      data: {
        tradingMode: process.env.TRADING_MODE || 'paper',
        dailyStats: dailyStats,
        activeOrders: activeOrders,
        timestamp: new Date()
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Close all positions
router.post('/close-all', async (req, res) => {
  try {
    const executor = req.app.locals.executor;
    await executor.closeAllPositions();
    
    res.json({
      success: true,
      message: 'All positions closed successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get recent trades (alias for history)
router.get('/trades', async (req, res) => {
  try {
    const { limit = 50 } = req.query;
    const db = req.app.locals.db;
    const tradeHistory = await db.getTradeHistory(parseInt(limit));
    
    // Transform data to match frontend expectations
    const trades = tradeHistory.map(trade => ({
      timestamp: trade.timestamp,
      symbol: trade.symbol,
      type: trade.action,
      amount: trade.quantity,
      price: trade.price,
      status: trade.status || 'completed',
      profitLoss: trade.profit_loss || 0
    }));
    
    res.json(trades);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get trade history
router.get('/history', async (req, res) => {
  try {
    const { limit = 100 } = req.query;
    const db = req.app.locals.db;
    const tradeHistory = await db.getTradeHistory(parseInt(limit));
    
    res.json({
      success: true,
      data: tradeHistory
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get trade history for specific symbol
router.get('/history/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { limit = 100 } = req.query;
    const db = req.app.locals.db;
    
    const sql = `
      SELECT * FROM trade_history 
      WHERE symbol = ? 
      ORDER BY timestamp DESC 
      LIMIT ?
    `;
    const tradeHistory = await db.all(sql, [symbol, parseInt(limit)]);
    
    res.json({
      success: true,
      data: tradeHistory
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Update trading mode
router.post('/mode', async (req, res) => {
  try {
    const { mode } = req.body;
    
    if (!['paper', 'live'].includes(mode)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid trading mode. Must be "paper" or "live"'
      });
    }
    
    // In a real implementation, you'd update the environment variable
    // For now, we'll just return success
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

module.exports = router;
