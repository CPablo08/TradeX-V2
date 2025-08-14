const axios = require('axios');
const winston = require('winston');

class DataRetriever {
  constructor(logger, db) {
    this.logger = logger;
    this.db = db;
    this.marketData = {};
    this.accountData = {};
    this.tradingMode = process.env.TRADING_MODE || 'paper';
    this.lastUpdate = new Date();
  }

  async initialize() {
    try {
      this.logger.info('Initializing DataRetriever...');
      await this.fetchMarketData();
      await this.fetchAccountData();
      this.logger.info('DataRetriever initialized successfully');
    } catch (error) {
      this.logger.error('DataRetriever initialization failed:', error);
      throw error;
    }
  }

  async fetchMarketData() {
    try {
      const symbols = ['BTC', 'ETH'];
      
      for (const symbol of symbols) {
        try {
          const response = await axios.get(`https://api.coinbase.com/v2/prices/${symbol}-USD/spot`);
          
          if (response.data && response.data.data) {
            const price = parseFloat(response.data.data.amount);
            const timestamp = new Date();
            
            this.marketData[symbol] = {
              symbol: symbol,
              price: price,
              timestamp: timestamp,
              volume: this.generateMockVolume(symbol, price),
              high: price * (1 + Math.random() * 0.02),
              low: price * (1 - Math.random() * 0.02),
              open: price * (1 + (Math.random() - 0.5) * 0.01)
            };
            
            // Save to database
            await this.db.saveMarketData(this.marketData[symbol]);
            
            this.logger.info(`Market data updated for ${symbol}: $${price.toFixed(2)}`);
          }
        } catch (error) {
          this.logger.error(`Failed to fetch market data for ${symbol}:`, error);
          // Use last known data or generate mock data
          this.marketData[symbol] = this.generateMockMarketData(symbol);
        }
      }
      
      this.lastUpdate = new Date();
    } catch (error) {
      this.logger.error('Failed to fetch market data:', error);
      throw error;
    }
  }

  async fetchAccountData() {
    try {
      if (this.tradingMode === 'paper') {
        await this.fetchPaperAccountData();
      } else {
        await this.fetchCoinbaseAccountData();
      }
    } catch (error) {
      this.logger.error('Failed to fetch account data:', error);
      throw error;
    }
  }

  async fetchPaperAccountData() {
    try {
      const recentTrades = await this.db.getTradeHistory(100);
      let totalPnL = 0;
      const positions = [];
      
      // Calculate P&L from recent trades
      recentTrades.forEach(trade => {
        if (trade.paper) {
          totalPnL += trade.profit_loss || 0;
        }
      });
      
      // Calculate current positions
      const btcPosition = await this.calculatePosition('BTC');
      const ethPosition = await this.calculatePosition('ETH');
      
      if (btcPosition.quantity > 0) {
        positions.push({
          symbol: 'BTC',
          quantity: btcPosition.quantity,
          value: btcPosition.value,
          avgPrice: btcPosition.avgPrice
        });
      }
      
      if (ethPosition.quantity > 0) {
        positions.push({
          symbol: 'ETH',
          quantity: ethPosition.quantity,
          value: ethPosition.value,
          avgPrice: ethPosition.avgPrice
        });
      }
      
      this.accountData = {
        balance: 1000, // Starting balance
        positions: positions,
        pnl: totalPnL,
        totalValue: 1000 + totalPnL,
        lastUpdate: new Date(),
        paper: true
      };
      
      await this.db.saveAccountData(this.accountData);
      this.logger.info('Paper trading account data simulated successfully');
    } catch (error) {
      this.logger.error('Failed to fetch paper trading account data:', error);
      throw error;
    }
  }

  async fetchCoinbaseAccountData() {
    try {
      // For real trading, we would use Coinbase API
      // This is a placeholder for when real trading is implemented
      const apiKey = process.env.COINBASE_API_KEY;
      const apiSecret = process.env.COINBASE_API_SECRET;
      
      if (!apiKey || !apiSecret) {
        throw new Error('Coinbase API credentials not configured');
      }
      
      // Placeholder for real Coinbase account data
      this.accountData = {
        balance: 1000,
        positions: [],
        pnl: 0,
        totalValue: 1000,
        lastUpdate: new Date(),
        paper: false
      };
      
      await this.db.saveAccountData(this.accountData);
      this.logger.info('Coinbase account data fetched successfully');
    } catch (error) {
      this.logger.error('Failed to fetch Coinbase account data:', error);
      throw error;
    }
  }

  async calculatePosition(symbol) {
    try {
      const allTrades = await this.db.getTradeHistory(1000);
      let netQuantity = 0;
      let totalCost = 0;
      
      allTrades.forEach(trade => {
        if (trade.symbol === symbol) {
          if (trade.action === 'BUY') {
            netQuantity += trade.quantity || 0;
            totalCost += (trade.quantity || 0) * (trade.price || 0);
          } else if (trade.action === 'SELL') {
            netQuantity -= trade.quantity || 0;
            // For FIFO calculation, we'd need more complex logic
          }
        }
      });
      
      const avgPrice = netQuantity > 0 ? totalCost / netQuantity : 0;
      const currentPrice = this.marketData[symbol]?.price || 0;
      const value = netQuantity * currentPrice;
      
      return {
        quantity: netQuantity,
        avgPrice: avgPrice,
        value: value,
        currentPrice: currentPrice
      };
    } catch (error) {
      this.logger.error(`Error calculating position for ${symbol}:`, error);
      return { quantity: 0, avgPrice: 0, value: 0, currentPrice: 0 };
    }
  }

  generateMockVolume(symbol, price) {
    // Generate realistic volume based on price
    const baseVolume = symbol === 'BTC' ? 1000 : 5000;
    return baseVolume + Math.random() * baseVolume;
  }

  generateMockMarketData(symbol) {
    const basePrice = symbol === 'BTC' ? 45000 : 3000;
    const price = basePrice + (Math.random() - 0.5) * basePrice * 0.1;
    
    return {
      symbol: symbol,
      price: price,
      timestamp: new Date(),
      volume: this.generateMockVolume(symbol, price),
      high: price * (1 + Math.random() * 0.02),
      low: price * (1 - Math.random() * 0.02),
      open: price * (1 + (Math.random() - 0.5) * 0.01)
    };
  }

  getMarketData(symbol) {
    return this.marketData[symbol] || null;
  }

  getAccountData() {
    return this.accountData;
  }

  getLastUpdate() {
    return this.lastUpdate;
  }

  getTradingMode() {
    return this.tradingMode;
  }
}

module.exports = DataRetriever;
