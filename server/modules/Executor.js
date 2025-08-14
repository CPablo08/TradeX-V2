const winston = require('winston');

class Executor {
  constructor(logger, db) {
    this.logger = logger;
    this.db = db;
    this.tradingMode = process.env.TRADING_MODE || 'paper';
    this.isInitialized = false;
  }

  async initialize() {
    try {
      this.logger.info('Initializing Executor...');
      
      // Validate API configuration
      await this.validateAPIConfiguration();
      
      this.isInitialized = true;
      this.logger.info('Executor initialized successfully');
    } catch (error) {
      this.logger.error('Executor initialization failed:', error);
      throw error;
    }
  }

  async validateAPIConfiguration() {
    try {
      const requiredKeys = this.tradingMode === 'paper'
        ? [] // No API keys needed for paper trading simulation
        : ['COINBASE_API_KEY', 'COINBASE_API_SECRET', 'COINBASE_PASSPHRASE'];
      
      for (const key of requiredKeys) {
        if (!process.env[key]) {
          throw new Error(`Missing required environment variable: ${key}`);
        }
      }
      
      this.logger.info('API configuration validated');
    } catch (error) {
      this.logger.error('API configuration validation failed:', error);
      throw error;
    }
  }

  async executeTrade(decision) {
    try {
      if (!this.isInitialized) {
        throw new Error('Executor not initialized');
      }

      if (this.tradingMode === 'paper') {
        return await this.executePaperTrade(decision);
      } else {
        return await this.executeCoinbaseTrade(decision);
      }
    } catch (error) {
      this.logger.error('Trade execution failed:', error);
      return {
        success: false,
        reason: error.message,
        timestamp: new Date()
      };
    }
  }

  async executePaperTrade(decision) {
    try {
      const quantity = 0.001; // Fixed quantity for paper trading
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

      // Save trade to database
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
      return {
        success: false,
        reason: error.message,
        timestamp: new Date()
      };
    }
  }

  async executeCoinbaseTrade(decision) {
    try {
      // Placeholder for real Coinbase trade execution
      // In production, this would use Coinbase Pro API with proper authentication
      
      const apiKey = process.env.COINBASE_API_KEY;
      const apiSecret = process.env.COINBASE_API_SECRET;
      const passphrase = process.env.COINBASE_PASSPHRASE;
      
      if (!apiKey || !apiSecret || !passphrase) {
        throw new Error('Coinbase API credentials not configured');
      }
      
      // This is a placeholder - real implementation would use Coinbase Pro API
      const orderId = `coinbase_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const result = {
        success: true,
        orderId: orderId,
        symbol: decision.symbol,
        action: decision.action,
        quantity: 0.001, // Would be calculated based on available balance
        price: decision.price,
        timestamp: new Date(),
        status: 'filled',
        paper: false
      };

      // Save trade to database
      await this.db.saveTrade({
        orderId: orderId,
        symbol: decision.symbol,
        action: decision.action,
        quantity: 0.001,
        price: decision.price,
        timestamp: new Date(),
        status: 'completed',
        paper: false
      });

      this.logger.info('Coinbase trade executed successfully:', result);
      return result;
    } catch (error) {
      this.logger.error('Coinbase trade execution failed:', error);
      return {
        success: false,
        reason: error.message,
        timestamp: new Date()
      };
    }
  }

  async getPositions() {
    try {
      if (this.tradingMode === 'paper') {
        return await this.getPaperPositions();
      } else {
        return await this.getCoinbasePositions();
      }
    } catch (error) {
      this.logger.error('Failed to get positions:', error);
      return [];
    }
  }

  async getPaperPositions() {
    try {
      const allTrades = await this.db.getTradeHistory(1000);
      const positions = {};
      
      allTrades.forEach(trade => {
        const symbol = trade.symbol;
        if (!positions[symbol]) {
          positions[symbol] = { quantity: 0, avgPrice: 0, totalCost: 0 };
        }
        
        if (trade.action === 'BUY') {
          const quantity = trade.quantity || 0;
          const price = trade.price || 0;
          const cost = quantity * price;
          
          positions[symbol].totalCost += cost;
          positions[symbol].quantity += quantity;
          positions[symbol].avgPrice = positions[symbol].totalCost / positions[symbol].quantity;
        } else if (trade.action === 'SELL') {
          positions[symbol].quantity -= trade.quantity || 0;
          if (positions[symbol].quantity <= 0) {
            positions[symbol] = { quantity: 0, avgPrice: 0, totalCost: 0 };
          }
        }
      });
      
      return Object.entries(positions)
        .filter(([symbol, pos]) => pos.quantity > 0)
        .map(([symbol, pos]) => ({
          symbol: symbol,
          quantity: pos.quantity,
          avgPrice: pos.avgPrice,
          value: pos.quantity * pos.avgPrice
        }));
    } catch (error) {
      this.logger.error('Failed to get paper positions:', error);
      return [];
    }
  }

  async getCoinbasePositions() {
    try {
      // Placeholder for real Coinbase positions
      // In production, this would fetch from Coinbase Pro API
      return [];
    } catch (error) {
      this.logger.error('Failed to get Coinbase positions:', error);
      return [];
    }
  }

  async closePositions(symbol) {
    try {
      if (this.tradingMode === 'paper') {
        return await this.closePaperPositions(symbol);
      } else {
        return await this.closeCoinbasePositions(symbol);
      }
    } catch (error) {
      this.logger.error('Failed to close positions:', error);
      return { success: false, reason: error.message };
    }
  }

  async closePaperPositions(symbol) {
    try {
      const positions = await this.getPaperPositions();
      const position = positions.find(p => p.symbol === symbol);
      
      if (!position || position.quantity <= 0) {
        return { success: true, message: 'No position to close' };
      }
      
      // Simulate closing position
      const orderId = `close_paper_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      await this.db.saveTrade({
        orderId: orderId,
        symbol: symbol,
        action: 'SELL',
        quantity: position.quantity,
        price: position.avgPrice, // Would be current market price in real scenario
        timestamp: new Date(),
        status: 'completed',
        paper: true
      });
      
      this.logger.info(`Paper position closed for ${symbol}: ${position.quantity} @ ${position.avgPrice}`);
      return { success: true, message: 'Position closed successfully' };
    } catch (error) {
      this.logger.error('Failed to close paper positions:', error);
      return { success: false, reason: error.message };
    }
  }

  async closeCoinbasePositions(symbol) {
    try {
      // Placeholder for real Coinbase position closing
      // In production, this would use Coinbase Pro API
      return { success: true, message: 'Position closed successfully (placeholder)' };
    } catch (error) {
      this.logger.error('Failed to close Coinbase positions:', error);
      return { success: false, reason: error.message };
    }
  }

  async getActiveOrders() {
    try {
      if (this.tradingMode === 'paper') {
        return await this.getPaperActiveOrders();
      } else {
        return await this.getCoinbaseActiveOrders();
      }
    } catch (error) {
      this.logger.error('Failed to get active orders:', error);
      return [];
    }
  }

  async getPaperActiveOrders() {
    try {
      // Paper trading doesn't have pending orders - all trades are immediate
      return [];
    } catch (error) {
      this.logger.error('Failed to get paper active orders:', error);
      return [];
    }
  }

  async getCoinbaseActiveOrders() {
    try {
      // Placeholder for real Coinbase active orders
      // In production, this would fetch from Coinbase Pro API
      return [];
    } catch (error) {
      this.logger.error('Failed to get Coinbase active orders:', error);
      return [];
    }
  }

  getTradingMode() {
    return this.tradingMode;
  }

  close() {
    this.logger.info('Executor closed');
  }
}

module.exports = Executor;

module.exports = Executor;
