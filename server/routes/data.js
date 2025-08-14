const express = require('express');
const router = express.Router();

// Get market data
router.get('/market', async (req, res) => {
  try {
    const dataRetriever = req.app.locals.dataRetriever;
    const marketData = await dataRetriever.getMarketData();
    
    res.json({
      success: true,
      data: marketData,
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get account data
router.get('/account', async (req, res) => {
  try {
    const dataRetriever = req.app.locals.dataRetriever;
    const accountData = await dataRetriever.getAccountData();
    
    res.json({
      success: true,
      data: accountData,
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get portfolio metrics (Total P&L, Total Trades, Portfolio Value)
router.get('/portfolio-metrics', async (req, res) => {
  try {
    const db = req.app.locals.db;
    
    // Get all trades from database
    const allTrades = await db.getTradeHistory(1000); // Get last 1000 trades
    
    // Calculate metrics
    let realizedPL = 0;
    let totalTrades = 0;
    let winningTrades = 0;
    let losingTrades = 0;
    
    // Calculate from actual trades
    const tradeMap = new Map(); // Track positions by symbol
    
    allTrades.forEach(trade => {
      totalTrades++;
      const symbol = trade.symbol;
      const quantity = trade.quantity;
      const price = trade.price;
      const action = trade.action;
      
      if (!tradeMap.has(symbol)) {
        tradeMap.set(symbol, []);
      }
      
      const symbolTrades = tradeMap.get(symbol);
      
      if (action === 'BUY') {
        symbolTrades.push({ quantity, price, action });
      } else if (action === 'SELL') {
        // Calculate P&L for this sell against previous buys
        let remainingQuantity = quantity;
        let tradePnL = 0;
        
        while (remainingQuantity > 0 && symbolTrades.length > 0) {
          const buyTrade = symbolTrades[0];
          const tradeQuantity = Math.min(remainingQuantity, buyTrade.quantity);
          
          // Calculate P&L: (sell_price - buy_price) * quantity
          const tradeProfit = (price - buyTrade.price) * tradeQuantity;
          tradePnL += tradeProfit;
          
          remainingQuantity -= tradeQuantity;
          buyTrade.quantity -= tradeQuantity;
          
          if (buyTrade.quantity <= 0) {
            symbolTrades.shift(); // Remove fully used buy trade
          }
        }
        
        realizedPL += tradePnL;
        
        if (tradePnL > 0) {
          winningTrades++;
        } else if (tradePnL < 0) {
          losingTrades++;
        }
      }
    });
    
    // Calculate current positions and their unrealized P&L
    let totalPositionValue = 0;
    let unrealizedPL = 0;
    
    for (const [symbol, trades] of tradeMap) {
      let netQuantity = 0;
      let totalCost = 0;
      
      trades.forEach(trade => {
        netQuantity += trade.quantity;
        totalCost += trade.quantity * trade.price;
      });
      
      if (netQuantity !== 0) {
        const avgPrice = totalCost / netQuantity;
        
        // Get current market price for this symbol
        let currentPrice = avgPrice; // Default to average price if we can't get current price
        
        // Try to get current price from market data
        try {
          const marketData = await db.getMarketData(symbol);
          if (marketData && marketData.price) {
            currentPrice = marketData.price;
          }
        } catch (error) {
          // If we can't get current price, use average price
          currentPrice = avgPrice;
        }
        
        const positionValue = netQuantity * currentPrice;
        const positionUnrealizedPL = positionValue - totalCost;
        
        totalPositionValue += positionValue;
        unrealizedPL += positionUnrealizedPL;
      }
    }
    
    // Calculate total P&L (realized + unrealized)
    const totalPL = realizedPL + unrealizedPL;
    
    // Calculate portfolio value (starting balance + total P&L)
    const startingBalance = 1000; // Paper trading starting balance
    const portfolioValue = startingBalance + totalPL;
    
    // Calculate win rate
    const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;
    
    const portfolioMetrics = {
      totalPL: totalPL, // Now includes both realized and unrealized P&L
      realizedPL: realizedPL,
      unrealizedPL: unrealizedPL,
      totalTrades: totalTrades,
      portfolioValue: portfolioValue,
      winningTrades: winningTrades,
      losingTrades: losingTrades,
      winRate: winRate,
      startingBalance: startingBalance,
      currentPositions: totalPositionValue,
      timestamp: new Date()
    };
    
    res.json({
      success: true,
      data: portfolioMetrics,
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get historical data for a symbol
router.get('/historical/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const { timeframe = '1D', limit = 100 } = req.query;
    
    const dataRetriever = req.app.locals.dataRetriever;
    const historicalData = await dataRetriever.getHistoricalData(symbol, timeframe, parseInt(limit));
    
    res.json({
      success: true,
      data: historicalData,
      symbol: symbol,
      timeframe: timeframe,
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get all data (market + account)
router.get('/all', async (req, res) => {
  try {
    const dataRetriever = req.app.locals.dataRetriever;
    const [marketData, accountData] = await Promise.all([
      dataRetriever.getMarketData(),
      dataRetriever.getAccountData()
    ]);
    
    res.json({
      success: true,
      data: {
        market: marketData,
        account: accountData
      },
      timestamp: new Date()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
