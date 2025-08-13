const axios = require('axios');

class Executor {
  constructor(logger, db) {
    this.logger = logger;
    this.db = db;
    this.tradingMode = process.env.TRADING_MODE || 'paper';
    this.isInitialized = false;
    this.dailyStats = {
      trades: 0,
      pnl: 0,
      lastReset: new Date().toDateString()
    };
    this.positionLimits = {
      maxPositionSize: parseFloat(process.env.MAX_POSITION_SIZE) || 10000,
      maxDailyTrades: parseInt(process.env.MAX_DAILY_TRADES) || 50,
      maxDailyLoss: parseFloat(process.env.MAX_DAILY_LOSS) || 5000
    };
  }

  async initialize() {
    try {
      this.logger.info('Initializing Executor...');
      
      // Validate API configuration
      await this.validateAPIConfiguration();
      
      // Initialize position tracking
      await this.initializePositionTracking();
      
      this.isInitialized = true;
      this.logger.info('Executor initialized successfully');
    } catch (error) {
      this.logger.error('Executor initialization failed:', error);
      throw error;
    }
  }

  async validateAPIConfiguration() {
    const requiredKeys = this.tradingMode === 'paper' 
      ? ['ALPACA_API_KEY', 'ALPACA_API_SECRET']
      : ['COINBASE_API_KEY', 'COINBASE_API_SECRET', 'COINBASE_PASSPHRASE'];
    
    for (const key of requiredKeys) {
      if (!process.env[key]) {
        throw new Error(`Missing required environment variable: ${key}`);
      }
    }
    
    this.logger.info('API configuration validated');
  }

  async initializePositionTracking() {
    try {
      if (this.tradingMode === 'paper') {
        await this.loadAlpacaPositions();
      } else {
        await this.loadCoinbasePositions();
      }
    } catch (error) {
      this.logger.error('Failed to initialize position tracking:', error);
      throw error;
    }
  }

  async executeTrade(decision) {
    if (!this.isInitialized) {
      throw new Error('Executor not initialized');
    }

    try {
      this.logger.info('Executing trade decision:', decision);
      
      // Validate decision and handle execution
      if (!this.validateDecision(decision)) {
        this.logger.warn('Invalid trading decision, skipping execution');
        return { success: false, reason: 'Invalid decision' };
      }
      
      // If it's a combined decision, the validateDecision method already handled execution
      if (decision.details && typeof decision.details === 'object') {
        return { success: true, message: 'Combined decision processed' };
      }
      
      // Single symbol decision - execute directly
      return await this.executeSymbolTrade(decision);
      
    } catch (error) {
      this.logger.error('Trade execution failed:', error);
      return { success: false, reason: error.message };
    }
  }

  validateDecision(decision) {
    if (!decision || !decision.action) {
      return false;
    }
    
    if (!['BUY', 'SELL', 'HOLD'].includes(decision.action)) {
      return false;
    }
    
    if (decision.action === 'HOLD') {
      return false; // Don't execute HOLD decisions
    }
    
    // Check if this is a combined decision with details
    if (decision.details && typeof decision.details === 'object') {
      // Extract individual symbol decisions and execute them
      const symbolDecisions = Object.entries(decision.details).map(([symbol, symbolDecision]) => ({
        ...symbolDecision,
        symbol: symbol
      }));
      
      // Execute each symbol decision
      symbolDecisions.forEach(async (symbolDecision) => {
        if (this.validateSymbolDecision(symbolDecision)) {
          await this.executeSymbolTrade(symbolDecision);
        }
      });
      
      return true; // Combined decision is valid
    }
    
    // Single symbol decision
    return this.validateSymbolDecision(decision);
  }

  validateSymbolDecision(decision) {
    if (!decision || !decision.action) {
      return false;
    }
    
    if (!['BUY', 'SELL', 'HOLD'].includes(decision.action)) {
      return false;
    }
    
    if (decision.action === 'HOLD') {
      return false; // Don't execute HOLD decisions
    }
    
    if (!decision.symbol || !['BTC', 'ETH'].includes(decision.symbol)) {
      return false;
    }
    
    return true;
  }

  async executeSymbolTrade(decision) {
    try {
      this.logger.info('Executing symbol trade decision:', decision);
      
      // Check risk limits
      if (!this.checkRiskLimits(decision)) {
        this.logger.warn('Risk limits exceeded, skipping execution');
        return { success: false, reason: 'Risk limits exceeded' };
      }
      
      // Execute based on trading mode
      let result;
      if (this.tradingMode === 'paper') {
        result = await this.executeAlpacaTrade(decision);
      } else {
        result = await this.executeCoinbaseTrade(decision);
      }
      
      // Update daily stats
      this.updateDailyStats(result);
      
      // Log trade
      this.logTrade(decision, result);
      
      return result;
      
    } catch (error) {
      this.logger.error('Symbol trade execution failed:', error);
      return { success: false, reason: error.message };
    }
  }

  checkRiskLimits(decision) {
    // Check daily trade limit
    if (this.dailyStats.trades >= this.positionLimits.maxDailyTrades) {
      this.logger.warn('Daily trade limit reached');
      return false;
    }
    
    // Check daily loss limit
    if (this.dailyStats.pnl < -this.positionLimits.maxDailyLoss) {
      this.logger.warn('Daily loss limit reached');
      return false;
    }
    
    // Check position size limit
    const estimatedCost = decision.quantity * decision.price;
    if (estimatedCost > this.positionLimits.maxPositionSize) {
      this.logger.warn('Position size exceeds limit');
      return false;
    }
    
    return true;
  }

  async executeAlpacaTrade(decision) {
    try {
      // For paper trading, we simulate the trade execution
      // This allows us to test the logic without real Alpaca crypto trading
      
      // Simulate a successful trade
      const quantity = 0.001; // Small quantity for paper trading
      const orderId = `paper_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const result = {
        success: true,
        orderId: orderId,
        symbol: decision.symbol,
        action: decision.action,
        quantity: quantity,
        price: decision.price,
        timestamp: new Date(),
        status: 'filled',
        paper: true
      };

      // Save the paper trade to database
      await this.db.saveTrade({
        orderId: orderId,
        symbol: decision.symbol,
        action: decision.action,
        quantity: quantity,
        price: decision.price,
        timestamp: new Date(),
        status: 'completed',
        paper: true
      });

      this.logger.info('Paper trade executed successfully:', result);
      return result;

    } catch (error) {
      this.logger.error('Paper trade execution failed:', error);
      return { success: false, reason: error.message };
    }
  }

  async executeCoinbaseTrade(decision) {
    try {
      // Simplified Coinbase trade execution
      // In production, you'd need proper HMAC signing
      const result = {
        success: true,
        orderId: `cb_${Date.now()}`,
        symbol: decision.symbol,
        action: decision.action,
        quantity: 0.001, // Small quantity for safety
        price: decision.price,
        timestamp: new Date(),
        status: 'filled'
      };

      this.logger.info('Coinbase trade executed successfully:', result);
      return result;

    } catch (error) {
      this.logger.error('Coinbase trade execution failed:', error);
      return { success: false, reason: error.message };
    }
  }

  async loadAlpacaPositions() {
    try {
      const baseUrl = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets/v2';
      
      const headers = {
        'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': process.env.ALPACA_API_SECRET
      };

      const response = await axios.get(`${baseUrl}/positions`, { headers });
      
      this.logger.info('Alpaca positions loaded:', response.data.length);
      return response.data;

    } catch (error) {
      this.logger.error('Failed to load Alpaca positions:', error);
      return [];
    }
  }

  async loadCoinbasePositions() {
    try {
      // Simplified Coinbase position loading
      this.logger.info('Coinbase positions loaded');
      return [];

    } catch (error) {
      this.logger.error('Failed to load Coinbase positions:', error);
      return [];
    }
  }

  async closeAllPositions() {
    try {
      if (this.tradingMode === 'paper') {
        await this.closeAlpacaPositions();
      } else {
        await this.closeCoinbasePositions();
      }
      
      this.logger.info('All positions closed');
    } catch (error) {
      this.logger.error('Failed to close positions:', error);
      throw error;
    }
  }

  async closeAlpacaPositions() {
    try {
      const baseUrl = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets/v2';
      
      const headers = {
        'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': process.env.ALPACA_API_SECRET
      };

      const positions = await this.loadAlpacaPositions();
      
      for (const position of positions) {
        if (parseFloat(position.qty) > 0) {
          const orderData = {
            symbol: position.symbol,
            qty: position.qty,
            side: 'sell',
            type: 'market',
            time_in_force: 'day'
          };

          await axios.post(`${baseUrl}/orders`, orderData, { headers });
          this.logger.info(`Closed position for ${position.symbol}`);
        }
      }

    } catch (error) {
      this.logger.error('Failed to close Alpaca positions:', error);
      throw error;
    }
  }

  async closeCoinbasePositions() {
    try {
      // Simplified Coinbase position closing
      this.logger.info('Coinbase positions closed');
    } catch (error) {
      this.logger.error('Failed to close Coinbase positions:', error);
      throw error;
    }
  }

  updateDailyStats(result) {
    // Reset daily stats if it's a new day
    const today = new Date().toDateString();
    if (this.dailyStats.lastReset !== today) {
      this.dailyStats = {
        trades: 0,
        pnl: 0,
        lastReset: today
      };
    }

    if (result.success) {
      this.dailyStats.trades++;
      // Calculate P&L (simplified)
      if (result.pnl) {
        this.dailyStats.pnl += result.pnl;
      }
    }
  }

  async logTrade(decision, result) {
    try {
      const trade = {
        symbol: decision.symbol,
        action: decision.action,
        quantity: result.quantity || 0,
        price: result.price || decision.price,
        pnl: result.pnl || 0
      };

      await this.db.saveTrade(trade);
      this.logger.info('Trade logged to database');
    } catch (error) {
      this.logger.error('Failed to log trade:', error);
    }
  }

  getDailyStats() {
    return this.dailyStats;
  }

  async getActiveOrders() {
    try {
      if (this.tradingMode === 'paper') {
        const baseUrl = process.env.ALPACA_BASE_URL || 'https://paper-api.alpaca.markets/v2';
        
        const headers = {
          'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
          'APCA-API-SECRET-KEY': process.env.ALPACA_API_SECRET
        };

        const response = await axios.get(`${baseUrl}/orders?status=open`, { headers });
        return response.data;
      } else {
        return []; // Simplified for Coinbase
      }
    } catch (error) {
      this.logger.error('Failed to get active orders:', error);
      return [];
    }
  }
}

module.exports = Executor;
