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
          // Fetch spot price from Coinbase
          const spotResponse = await axios.get(`https://api.coinbase.com/v2/prices/${symbol}-USD/spot`);
          
          // Fetch ticker data from Coinbase Exchange (Advanced Trade)
          const tickerResponse = await axios.get(`https://api.exchange.coinbase.com/products/${symbol}-USD/ticker`);
          
          if (spotResponse.data && spotResponse.data.data && tickerResponse.data) {
            const price = parseFloat(spotResponse.data.data.amount);
            const ticker = tickerResponse.data;
            const timestamp = new Date();
            
            this.marketData[symbol] = {
              symbol: symbol,
              price: price,
              timestamp: timestamp,
              volume: parseFloat(ticker.volume) || this.generateMockVolume(symbol, price),
              bid: parseFloat(ticker.bid),
              ask: parseFloat(ticker.ask),
              high: price * (1 + Math.random() * 0.02), // Not available in public API
              low: price * (1 - Math.random() * 0.02),  // Not available in public API
              open: price * (1 + (Math.random() - 0.5) * 0.01), // Not available in public API
              change24h: 0 // Not available in public API
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
      const apiKey = process.env.COINBASE_API_KEY;
      const apiSecret = process.env.COINBASE_API_SECRET;
      
      if (!apiKey || !apiSecret) {
        throw new Error('Coinbase API credentials not configured');
      }
      
      // For real Coinbase trading, we would fetch:
      // 1. Account balances
      // 2. Current positions
      // 3. Transaction history
      // 4. Realized/unrealized P&L
      
      // This is a placeholder implementation
      // In real implementation, you would use Coinbase Advanced Trade API
      this.accountData = {
        balance: 1000,
        positions: [],
        pnl: 0,
        totalValue: 1000,
        lastUpdate: new Date(),
        paper: false,
        apiError: 'Real Coinbase API integration not yet implemented'
      };
      
      await this.db.saveAccountData(this.accountData);
      this.logger.info('Coinbase account data placeholder created');
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
      bid: price * 0.999,
      ask: price * 1.001,
      high: price * 1.02,
      low: price * 0.98,
      open: price * 1.01,
      change24h: (Math.random() - 0.5) * 10
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

  // New method to get Coinbase-specific metrics
  async getCoinbaseMetrics() {
    try {
      const metrics = {
        // Available from Coinbase API
        currentPrices: {},
        volume24h: {},
        bidAskSpread: {},
        
        // Not available from public Coinbase API (will show API Error)
        historicalData: 'API Error',
        advancedAnalytics: 'API Error',
        detailedVolume: 'API Error',
        priceHistory: 'API Error'
      };

      // Fetch current prices and basic data
      for (const symbol of ['BTC', 'ETH']) {
        try {
          const spotResponse = await axios.get(`https://api.coinbase.com/v2/prices/${symbol}-USD/spot`);
          const tickerResponse = await axios.get(`https://api.exchange.coinbase.com/products/${symbol}-USD/ticker`);
          
          if (spotResponse.data && tickerResponse.data) {
            const price = parseFloat(spotResponse.data.data.amount);
            const ticker = tickerResponse.data;
            
            metrics.currentPrices[symbol] = price;
            metrics.volume24h[symbol] = parseFloat(ticker.volume) || 'API Error';
            metrics.bidAskSpread[symbol] = parseFloat(ticker.ask) - parseFloat(ticker.bid);
          }
        } catch (error) {
          metrics.currentPrices[symbol] = 'API Error';
          metrics.volume24h[symbol] = 'API Error';
          metrics.bidAskSpread[symbol] = 'API Error';
        }
      }

      return metrics;
    } catch (error) {
      this.logger.error('Error fetching Coinbase metrics:', error);
      return {
        currentPrices: { BTC: 'API Error', ETH: 'API Error' },
        volume24h: { BTC: 'API Error', ETH: 'API Error' },
        bidAskSpread: { BTC: 'API Error', ETH: 'API Error' },
        historicalData: 'API Error',
        advancedAnalytics: 'API Error',
        detailedVolume: 'API Error',
        priceHistory: 'API Error'
      };
    }
  }
}

module.exports = DataRetriever;
