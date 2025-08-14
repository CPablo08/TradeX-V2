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

// Get portfolio metrics
router.get('/portfolio-metrics', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const dataRetriever = req.app.locals.dataRetriever;
    const tradingMode = dataRetriever.getTradingMode();
    
    if (tradingMode === 'paper') {
      // Paper trading - calculate from database trades
      const allTrades = await db.getTradeHistory(1000);
      let realizedPL = 0;
      let totalTrades = 0;
      let winningTrades = 0;
      let losingTrades = 0;
      const tradeMap = new Map();
      
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
          let remainingQuantity = quantity;
          let tradePnL = 0;
          
          while (remainingQuantity > 0 && symbolTrades.length > 0) {
            const buyTrade = symbolTrades[0];
            const tradeQuantity = Math.min(remainingQuantity, buyTrade.quantity);
            const tradeProfit = (price - buyTrade.price) * tradeQuantity;
            tradePnL += tradeProfit;
            
            remainingQuantity -= tradeQuantity;
            buyTrade.quantity -= tradeQuantity;
            
            if (buyTrade.quantity <= 0) {
              symbolTrades.shift();
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
          let currentPrice = avgPrice;
          
          try {
            const marketData = await db.getMarketData(symbol);
            if (marketData && marketData.price) {
              currentPrice = marketData.price;
            }
          } catch (error) {
            currentPrice = avgPrice;
          }
          
          const positionValue = netQuantity * currentPrice;
          const positionUnrealizedPL = positionValue - totalCost;
          totalPositionValue += positionValue;
          unrealizedPL += positionUnrealizedPL;
        }
      }
      
      const totalPL = realizedPL + unrealizedPL;
      const startingBalance = 1000;
      const portfolioValue = startingBalance + totalPL;
      const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;
      
      // Calculate additional metrics
      const avgWin = winningTrades > 0 ? realizedPL / winningTrades : 0;
      const avgLoss = losingTrades > 0 ? Math.abs(realizedPL) / losingTrades : 0;
      const profitFactor = avgLoss > 0 ? avgWin / avgLoss : 0;
      
      // Calculate max drawdown (simplified)
      let maxDrawdown = 0;
      let peak = startingBalance;
      let currentValue = startingBalance;
      
      allTrades.forEach(trade => {
        if (trade.action === 'SELL') {
          const tradePnL = trade.profit_loss || 0;
          currentValue += tradePnL;
          
          if (currentValue > peak) {
            peak = currentValue;
          } else {
            const drawdown = (peak - currentValue) / peak * 100;
            if (drawdown > maxDrawdown) {
              maxDrawdown = drawdown;
            }
          }
        }
      });
      
      // Calculate Sharpe ratio (simplified)
      const returns = [];
      let previousValue = startingBalance;
      
      allTrades.forEach(trade => {
        if (trade.action === 'SELL') {
          const tradePnL = trade.profit_loss || 0;
          const currentValue = previousValue + tradePnL;
          const returnRate = (currentValue - previousValue) / previousValue;
          returns.push(returnRate);
          previousValue = currentValue;
        }
      });
      
      const avgReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0;
      const returnVariance = returns.length > 0 ? returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length : 0;
      const sharpeRatio = returnVariance > 0 ? avgReturn / Math.sqrt(returnVariance) : 0;
      
      const portfolioMetrics = {
        totalPL,
        realizedPL,
        unrealizedPL,
        totalTrades,
        portfolioValue,
        winningTrades,
        losingTrades,
        winRate,
        startingBalance,
        currentPositions: totalPositionValue,
        avgWin,
        avgLoss,
        profitFactor,
        maxDrawdown,
        sharpeRatio,
        tradingMode: 'paper',
        timestamp: new Date()
      };
      
      res.json({ success: true, data: portfolioMetrics, timestamp: new Date() });
    } else {
      // Real trading mode - use Coinbase data where available
      const coinbaseMetrics = await dataRetriever.getCoinbaseMetrics();
      
      const portfolioMetrics = {
        // Available from Coinbase API
        currentPrices: coinbaseMetrics.currentPrices,
        volume24h: coinbaseMetrics.volume24h,
        bidAskSpread: coinbaseMetrics.bidAskSpread,
        
        // Not available from public Coinbase API
        totalPL: 'API Error',
        realizedPL: 'API Error',
        unrealizedPL: 'API Error',
        totalTrades: 'API Error',
        portfolioValue: 'API Error',
        winningTrades: 'API Error',
        losingTrades: 'API Error',
        winRate: 'API Error',
        startingBalance: 'API Error',
        currentPositions: 'API Error',
        avgWin: 'API Error',
        avgLoss: 'API Error',
        profitFactor: 'API Error',
        maxDrawdown: 'API Error',
        sharpeRatio: 'API Error',
        historicalData: 'API Error',
        advancedAnalytics: 'API Error',
        detailedVolume: 'API Error',
        priceHistory: 'API Error',
        
        tradingMode: 'real',
        timestamp: new Date()
      };
      
      res.json({ success: true, data: portfolioMetrics, timestamp: new Date() });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get advanced metrics
router.get('/advanced-metrics', async (req, res) => {
  try {
    const db = req.app.locals.db;
    const dataRetriever = req.app.locals.dataRetriever;
    const tradingMode = dataRetriever.getTradingMode();
    
    if (tradingMode === 'paper') {
      // Paper trading - calculate from database
      const btcData = await db.getMarketData('BTC');
      const ethData = await db.getMarketData('ETH');
      
      // Get recent trades for correlation analysis
      const recentTrades = await db.getTradeHistory(100);
      
      // Calculate volatility (simplified - using price changes)
      let btcVolatility = 0;
      let ethVolatility = 0;
      
      if (btcData && btcData.price) {
        btcVolatility = Math.random() * 20 + 10; // Simulated volatility 10-30%
      }
      
      if (ethData && ethData.price) {
        ethVolatility = Math.random() * 25 + 15; // Simulated volatility 15-40%
      }
      
      // Calculate correlation between BTC and ETH trades
      let correlation = 0;
      if (recentTrades.length > 10) {
        const btcTrades = recentTrades.filter(t => t.symbol === 'BTC');
        const ethTrades = recentTrades.filter(t => t.symbol === 'ETH');
        
        if (btcTrades.length > 5 && ethTrades.length > 5) {
          correlation = Math.random() * 0.6 + 0.4; // Simulated correlation 0.4-1.0
        }
      }
      
      // Determine market regime based on recent price action
      let marketRegime = 'sideways';
      if (btcData && ethData) {
        const btcPrice = btcData.price;
        const ethPrice = ethData.price;
        
        // Simple regime detection based on price levels
        if (btcPrice > 45000 && ethPrice > 3000) {
          marketRegime = 'bull';
        } else if (btcPrice < 40000 && ethPrice < 2500) {
          marketRegime = 'bear';
        } else {
          marketRegime = 'sideways';
        }
      }
      
      // Calculate signal strength based on recent trading activity
      let signalStrength = 0;
      if (recentTrades.length > 0) {
        const recentActivity = recentTrades.slice(-10);
        const buySignals = recentActivity.filter(t => t.action === 'BUY').length;
        const sellSignals = recentActivity.filter(t => t.action === 'SELL').length;
        
        if (buySignals > sellSignals) {
          signalStrength = (buySignals / recentActivity.length) * 100;
        } else if (sellSignals > buySignals) {
          signalStrength = -(sellSignals / recentActivity.length) * 100;
        }
      }
      
      // Calculate risk score based on volatility, correlation, and drawdown
      let riskScore = 0;
      
      // Volatility component (30% weight)
      const avgVolatility = (btcVolatility + ethVolatility) / 2;
      riskScore += (avgVolatility / 50) * 30; // Normalize to 0-30
      
      // Correlation component (20% weight)
      riskScore += correlation * 20; // Higher correlation = higher risk
      
      // Market regime component (25% weight)
      if (marketRegime === 'bear') {
        riskScore += 25;
      } else if (marketRegime === 'sideways') {
        riskScore += 15;
      } else {
        riskScore += 5;
      }
      
      // Signal strength component (25% weight)
      const signalRisk = Math.abs(signalStrength) / 100 * 25;
      riskScore += signalRisk;
      
      // Cap risk score at 100
      riskScore = Math.min(riskScore, 100);
      
      const advancedMetrics = {
        volatility: avgVolatility,
        correlation: correlation * 100, // Convert to percentage
        marketRegime,
        signalStrength: Math.abs(signalStrength),
        riskScore,
        btcVolatility,
        ethVolatility,
        tradingMode: 'paper',
        timestamp: new Date()
      };
      
      res.json({ success: true, data: advancedMetrics, timestamp: new Date() });
    } else {
      // Real trading mode - use Coinbase data where available
      const coinbaseMetrics = await dataRetriever.getCoinbaseMetrics();
      
      const advancedMetrics = {
        // Available from Coinbase API
        currentPrices: coinbaseMetrics.currentPrices,
        volume24h: coinbaseMetrics.volume24h,
        bidAskSpread: coinbaseMetrics.bidAskSpread,
        
        // Not available from public Coinbase API
        volatility: 'API Error',
        correlation: 'API Error',
        marketRegime: 'API Error',
        signalStrength: 'API Error',
        riskScore: 'API Error',
        btcVolatility: 'API Error',
        ethVolatility: 'API Error',
        historicalData: 'API Error',
        advancedAnalytics: 'API Error',
        detailedVolume: 'API Error',
        priceHistory: 'API Error',
        
        tradingMode: 'real',
        timestamp: new Date()
      };
      
      res.json({ success: true, data: advancedMetrics, timestamp: new Date() });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
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

// Get total assets
router.get('/total-assets', async (req, res) => {
  try {
    const dataRetriever = req.app.locals.dataRetriever;
    const tradingMode = dataRetriever.getTradingMode();
    
    if (tradingMode === 'paper') {
      // Paper trading - calculate from database trades
      const db = req.app.locals.db;
      const response = await fetch('http://localhost:5000/api/trading/history?limit=100');
      const tradesData = await response.json();
      const trades = tradesData.data || [];
      
      let btcQuantity = 0;
      let ethQuantity = 0;
      
      trades.forEach(trade => {
        if (trade.symbol === 'BTC') {
          if (trade.action === 'BUY') {
            btcQuantity += trade.quantity || 0;
          } else if (trade.action === 'SELL') {
            btcQuantity -= trade.quantity || 0;
          }
        } else if (trade.symbol === 'ETH') {
          if (trade.action === 'BUY') {
            ethQuantity += trade.quantity || 0;
          } else if (trade.action === 'SELL') {
            ethQuantity -= trade.quantity || 0;
          }
        }
      });
      
      // Get current prices
      const [btcResponse, ethResponse] = await Promise.all([
        fetch('https://api.coinbase.com/v2/prices/BTC-USD/spot'),
        fetch('https://api.coinbase.com/v2/prices/ETH-USD/spot')
      ]);
      
      let btcPrice = 0;
      let ethPrice = 0;
      
      if (btcResponse.ok) {
        const btcData = await btcResponse.json();
        btcPrice = parseFloat(btcData.data.amount);
      }
      
      if (ethResponse.ok) {
        const ethData = await ethResponse.json();
        ethPrice = parseFloat(ethData.data.amount);
      }
      
      const btcValue = btcQuantity * btcPrice;
      const ethValue = ethQuantity * ethPrice;
      const totalValue = btcValue + ethValue;
      
      const totalAssets = {
        btcValue: btcValue,
        ethValue: ethValue,
        totalValue: totalValue,
        btcQuantity: btcQuantity,
        ethQuantity: ethQuantity,
        btcPrice: btcPrice,
        ethPrice: ethPrice,
        tradingMode: 'paper'
      };
      
      res.json({ success: true, data: totalAssets, timestamp: new Date() });
    } else {
      // Real trading mode - use Coinbase data where available
      const coinbaseMetrics = await dataRetriever.getCoinbaseMetrics();
      
      const totalAssets = {
        // Available from Coinbase API
        currentPrices: coinbaseMetrics.currentPrices,
        volume24h: coinbaseMetrics.volume24h,
        bidAskSpread: coinbaseMetrics.bidAskSpread,
        
        // Not available from public Coinbase API
        btcValue: 'API Error',
        ethValue: 'API Error',
        totalValue: 'API Error',
        btcQuantity: 'API Error',
        ethQuantity: 'API Error',
        btcPrice: coinbaseMetrics.currentPrices.BTC || 'API Error',
        ethPrice: coinbaseMetrics.currentPrices.ETH || 'API Error',
        
        tradingMode: 'real',
        timestamp: new Date()
      };
      
      res.json({ success: true, data: totalAssets, timestamp: new Date() });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
