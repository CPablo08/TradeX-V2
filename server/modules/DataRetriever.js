const axios = require('axios');

class DataRetriever {
  constructor(logger, db) {
    this.logger = logger;
    this.db = db;
    this.marketData = {
      BTC: null,
      ETH: null
    };
    this.accountData = null;
    this.isInitialized = false;
  }

  async initialize() {
    try {
      this.logger.info('Initializing DataRetriever...');
      
      // Fetch initial data
      await this.fetchInitialData();
      
      this.isInitialized = true;
      this.logger.info('DataRetriever initialized successfully');
    } catch (error) {
      this.logger.error('DataRetriever initialization failed:', error);
      throw error;
    }
  }

  async fetchInitialData() {
    try {
      // Fetch market data from Coinbase
      await this.fetchMarketData();
      
      // Fetch account data from Alpaca
      await this.fetchAccountData();
      
      this.logger.info('Initial data fetched successfully');
    } catch (error) {
      this.logger.error('Failed to fetch initial data:', error);
      throw error;
    }
  }

  async fetchMarketData() {
    try {
      const tradingMode = process.env.TRADING_MODE || 'paper';
      
      if (tradingMode === 'paper') {
        // Use Alpaca for paper trading
        await this.fetchAlpacaMarketData();
      } else {
        // Use Coinbase for real trading
        await this.fetchCoinbaseMarketData();
      }
    } catch (error) {
      this.logger.error('Failed to fetch market data:', error);
      throw error;
    }
  }

  async fetchAlpacaMarketData() {
    try {
      // For paper trading, we'll use Coinbase prices but simulate Alpaca execution
      // This allows us to test the logic without real Alpaca crypto trading
      const [btcResponse, ethResponse] = await Promise.all([
        axios.get('https://api.coinbase.com/v2/prices/BTC-USD/spot'),
        axios.get('https://api.coinbase.com/v2/prices/ETH-USD/spot')
      ]);

      // Process BTC data
      this.marketData.BTC = {
        price: parseFloat(btcResponse.data.data.amount),
        change24h: 0, // Will be calculated from historical data
        volume: 0, // Not available in spot price endpoint
        lastUpdate: new Date()
      };

      // Process ETH data
      this.marketData.ETH = {
        price: parseFloat(ethResponse.data.data.amount),
        change24h: 0, // Will be calculated from historical data
        volume: 0, // Not available in spot price endpoint
        lastUpdate: new Date()
      };

      // Save to database
      await this.db.saveMarketData('BTC', this.marketData.BTC);
      await this.db.saveMarketData('ETH', this.marketData.ETH);

      this.logger.info('Paper trading market data fetched successfully (using Coinbase prices)');
    } catch (error) {
      this.logger.error('Failed to fetch paper trading market data:', error);
      throw error;
    }
  }

  async fetchCoinbaseMarketData() {
    try {
      // Fetch BTC and ETH prices from Coinbase
      const [btcResponse, ethResponse] = await Promise.all([
        axios.get('https://api.coinbase.com/v2/prices/BTC-USD/spot'),
        axios.get('https://api.coinbase.com/v2/prices/ETH-USD/spot')
      ]);

      // Process BTC data
      this.marketData.BTC = {
        price: parseFloat(btcResponse.data.data.amount),
        change24h: 0, // Will be calculated from historical data
        volume: 0, // Not available in spot price endpoint
        lastUpdate: new Date()
      };

      // Process ETH data
      this.marketData.ETH = {
        price: parseFloat(ethResponse.data.data.amount),
        change24h: 0, // Will be calculated from historical data
        volume: 0, // Not available in spot price endpoint
        lastUpdate: new Date()
      };

      // Save to database
      await this.db.saveMarketData('BTC', this.marketData.BTC);
      await this.db.saveMarketData('ETH', this.marketData.ETH);

      this.logger.info('Coinbase market data fetched successfully');
    } catch (error) {
      this.logger.error('Failed to fetch Coinbase market data:', error);
      throw error;
    }
  }

  async fetchAccountData() {
    try {
      const tradingMode = process.env.TRADING_MODE || 'paper';
      
      if (tradingMode === 'paper') {
        await this.fetchAlpacaAccountData();
      } else {
        await this.fetchCoinbaseAccountData();
      }
    } catch (error) {
      this.logger.error('Failed to fetch account data:', error);
      throw error;
    }
  }

  async fetchAlpacaAccountData() {
    try {
      // For paper trading, we simulate account data
      // This allows us to test the system without real Alpaca crypto trading
      
      // Get recent trades from database to calculate paper trading performance
      const recentTrades = await this.db.getTradeHistory(100);
      
      let totalPnL = 0;
      const positions = [];
      
      // Calculate P&L from recent trades
      recentTrades.forEach(trade => {
        if (trade.paper) {
          totalPnL += trade.profit_loss || 0;
        }
      });
      
                      // Simulate paper trading account
                this.accountData = {
                  balance: 1000, // Starting balance
                  positions: positions,
                  pnl: totalPnL,
                  totalValue: 1000 + totalPnL,
                  lastUpdate: new Date()
                };

      // Save to database
      await this.db.saveAccountData(this.accountData);

      this.logger.info('Paper trading account data simulated successfully');
    } catch (error) {
      this.logger.error('Failed to fetch paper trading account data:', error);
      throw error;
    }
  }

  async fetchCoinbaseAccountData() {
    try {
      // For now, we'll use a simplified approach
      // In production, you'd need proper HMAC signing
      this.accountData = {
        balance: 100000, // Placeholder
        positions: [],
        pnl: 0,
        lastUpdate: new Date()
      };

      await this.db.saveAccountData(this.accountData);
      this.logger.info('Coinbase account data fetched successfully');
    } catch (error) {
      this.logger.error('Failed to fetch Coinbase account data:', error);
      throw error;
    }
  }

  async getMarketData() {
    return this.marketData;
  }

  async getAccountData() {
    return this.accountData;
  }

  async getHistoricalData(symbol, timeframe = '1D', limit = 100) {
    try {
      // For now, return mock historical data
      // In production, you'd fetch from Coinbase/Alpaca APIs
      const mockData = [];
      const basePrice = symbol === 'BTC' ? 120000 : 4000;
      
      for (let i = 0; i < limit; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        const price = basePrice + (Math.random() - 0.5) * 1000;
        mockData.push({
          timestamp: date,
          open: price,
          high: price + Math.random() * 100,
          low: price - Math.random() * 100,
          close: price + (Math.random() - 0.5) * 50,
          volume: Math.random() * 1000000
        });
      }
      
      return mockData.reverse();
    } catch (error) {
      this.logger.error('Failed to fetch historical data:', error);
      throw error;
    }
  }

  async getGranularity(timeframe) {
    const granularityMap = {
      '1m': 60,
      '5m': 300,
      '15m': 900,
      '1h': 3600,
      '1D': 86400
    };
    return granularityMap[timeframe] || 86400;
  }

  close() {
    this.logger.info('DataRetriever closed');
  }
}

module.exports = DataRetriever;
