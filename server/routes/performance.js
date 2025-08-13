const express = require('express');
const router = express.Router();

// Get performance metrics for a specific date
router.get('/metrics/:date', async (req, res) => {
  try {
    const { date } = req.params;
    const db = req.app.locals.db;
    const metrics = await db.getPerformanceMetrics(date);
    
    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get performance history
router.get('/history', async (req, res) => {
  try {
    const { limit = 30 } = req.query;
    const db = req.app.locals.db;
    
    const sql = `
      SELECT * FROM performance_metrics 
      ORDER BY date DESC 
      LIMIT ?
    `;
    const history = await db.all(sql, [parseInt(limit)]);
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get performance summary
router.get('/summary', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const executor = req.app.locals.executor;
    
    // Get today's date
    const today = new Date().toISOString().split('T')[0];
    
    // Get today's metrics
    const todayMetrics = await db.getPerformanceMetrics(today);
    
    // Get daily stats from executor
    const dailyStats = executor.getDailyStats();
    
    // Calculate summary
    const summary = {
      today: todayMetrics || {
        total_trades: 0,
        winning_trades: 0,
        total_pnl: 0,
        win_rate: 0
      },
      dailyStats: dailyStats,
      timestamp: new Date()
    };
    
    res.json({
      success: true,
      data: summary
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get analytics data
router.get('/analytics', async (req, res) => {
  try {
    const { days = 30 } = req.query;
    const db = req.app.locals.db;
    
    // Get trade history for analytics
    const tradeHistory = await db.getTradeHistory(parseInt(days) * 10); // More data for analytics
    
    // Calculate analytics
    const analytics = calculateAnalytics(tradeHistory);
    
    res.json({
      success: true,
      data: analytics
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get system logs
router.get('/logs', async (req, res) => {
  try {
    const { limit = 100, level } = req.query;
    const db = req.app.locals.db;
    
    let sql = 'SELECT * FROM system_logs';
    let params = [];
    
    if (level) {
      sql += ' WHERE level = ?';
      params.push(level);
    }
    
    sql += ' ORDER BY timestamp DESC LIMIT ?';
    params.push(parseInt(limit));
    
    const logs = await db.all(sql, params);
    
    res.json({
      success: true,
      data: logs
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get system stats
router.get('/stats', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const watchdog = req.app.locals.watchdog;
    
    // Get database stats
    const dbStats = await db.getDatabaseStats();
    
    // Get system info
    const systemInfo = watchdog.getSystemInfo();
    
    // Get error count
    const errorCount = watchdog.getErrorCount();
    
    const stats = {
      database: dbStats,
      system: systemInfo,
      errors: errorCount,
      timestamp: new Date()
    };
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Helper function to calculate analytics
function calculateAnalytics(tradeHistory) {
  if (!tradeHistory || tradeHistory.length === 0) {
    return {
      totalTrades: 0,
      winningTrades: 0,
      losingTrades: 0,
      winRate: 0,
      totalPnl: 0,
      averagePnl: 0,
      bestTrade: 0,
      worstTrade: 0,
      profitFactor: 0,
      sharpeRatio: 0
    };
  }
  
  const trades = tradeHistory.filter(trade => trade.pnl !== null);
  
  if (trades.length === 0) {
    return {
      totalTrades: 0,
      winningTrades: 0,
      losingTrades: 0,
      winRate: 0,
      totalPnl: 0,
      averagePnl: 0,
      bestTrade: 0,
      worstTrade: 0,
      profitFactor: 0,
      sharpeRatio: 0
    };
  }
  
  const totalTrades = trades.length;
  const winningTrades = trades.filter(trade => trade.pnl > 0).length;
  const losingTrades = trades.filter(trade => trade.pnl < 0).length;
  const winRate = (winningTrades / totalTrades) * 100;
  
  const totalPnl = trades.reduce((sum, trade) => sum + trade.pnl, 0);
  const averagePnl = totalPnl / totalTrades;
  
  const bestTrade = Math.max(...trades.map(trade => trade.pnl));
  const worstTrade = Math.min(...trades.map(trade => trade.pnl));
  
  const grossProfit = trades
    .filter(trade => trade.pnl > 0)
    .reduce((sum, trade) => sum + trade.pnl, 0);
  
  const grossLoss = Math.abs(trades
    .filter(trade => trade.pnl < 0)
    .reduce((sum, trade) => sum + trade.pnl, 0));
  
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : 0;
  
  // Simplified Sharpe ratio calculation
  const returns = trades.map(trade => trade.pnl);
  const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
  const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
  const sharpeRatio = variance > 0 ? avgReturn / Math.sqrt(variance) : 0;
  
  return {
    totalTrades,
    winningTrades,
    losingTrades,
    winRate: Math.round(winRate * 100) / 100,
    totalPnl: Math.round(totalPnl * 100) / 100,
    averagePnl: Math.round(averagePnl * 100) / 100,
    bestTrade: Math.round(bestTrade * 100) / 100,
    worstTrade: Math.round(worstTrade * 100) / 100,
    profitFactor: Math.round(profitFactor * 100) / 100,
    sharpeRatio: Math.round(sharpeRatio * 100) / 100
  };
}

module.exports = router;
