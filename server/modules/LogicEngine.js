const technicalIndicators = require('technicalindicators');

class LogicEngine {
  constructor(logger, db) {
    this.logger = logger;
    this.db = db;
    this.strategies = {
      BTC: null,
      ETH: null
    };
    this.isInitialized = false;
    this.historicalData = {
      BTC: [],
      ETH: []
    };
  }

  async initialize() {
    try {
      this.logger.info('Initializing LogicEngine...');
      
      // Load default strategies
      await this.loadDefaultStrategies();
      
      this.isInitialized = true;
      this.logger.info('LogicEngine initialized successfully');
    } catch (error) {
      this.logger.error('LogicEngine initialization failed:', error);
      throw error;
    }
  }

  async loadDefaultStrategies() {
    try {
      // Create default moving average crossover strategy
      const defaultStrategy = {
        name: 'MA Crossover Strategy',
        code: `
// Simple Moving Average Crossover Strategy
// Buy when fast MA crosses above slow MA
// Sell when fast MA crosses below slow MA

fastMA = sma(close, 10)
slowMA = sma(close, 20)

buySignal = fastMA > slowMA and fastMA[1] <= slowMA[1]
sellSignal = fastMA < slowMA and fastMA[1] >= slowMA[1]

if buySignal
    return { action: 'BUY', reason: 'Fast MA crossed above Slow MA', confidence: 75 }
if sellSignal
    return { action: 'SELL', reason: 'Fast MA crossed below Slow MA', confidence: 75 }

return { action: 'HOLD', reason: 'No crossover signal', confidence: 0 }
        `,
        isActive: true
      };

      // Save default strategies for both BTC and ETH
      await this.db.saveStrategy('BTC', defaultStrategy.name, defaultStrategy.code);
      await this.db.saveStrategy('ETH', defaultStrategy.name, defaultStrategy.code);
      
      // Load strategies from database
      this.strategies.BTC = await this.db.getStrategy('BTC');
      this.strategies.ETH = await this.db.getStrategy('ETH');
      
      this.logger.info('Default strategies loaded successfully');
    } catch (error) {
      this.logger.error('Failed to load default strategies:', error);
      throw error;
    }
  }

  async updateStrategy(symbol, name, code) {
    try {
      await this.db.saveStrategy(symbol, name, code);
      this.strategies[symbol] = await this.db.getStrategy(symbol);
      this.logger.info(`Strategy updated for ${symbol}`);
    } catch (error) {
      this.logger.error(`Failed to update strategy for ${symbol}:`, error);
      throw error;
    }
  }

  validatePineScript(code) {
    try {
      // Basic Pine Script validation
      const requiredKeywords = ['strategy', 'sma', 'close'];
      const hasRequiredKeywords = requiredKeywords.some(keyword => 
        code.toLowerCase().includes(keyword.toLowerCase())
      );
      
      if (!hasRequiredKeywords) {
        return { valid: false, error: 'Missing required Pine Script keywords' };
      }
      
      return { valid: true };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }

  async processData() {
    try {
      const decisions = {};
      
      // Process each symbol
      for (const symbol of ['BTC', 'ETH']) {
        const decision = await this.evaluateStrategy(symbol);
        decisions[symbol] = decision;
      }
      
      // Combine decisions into overall action
      const combinedDecision = this.combineDecisions(decisions);
      
      this.logger.info('Trading decision generated:', combinedDecision);
      return combinedDecision;
      
    } catch (error) {
      this.logger.error('Error processing data:', error);
      return {
        action: 'HOLD',
        reason: 'Strategy evaluation error',
        timestamp: new Date(),
        confidence: 0,
        details: {}
      };
    }
  }

  async evaluateStrategy(symbol) {
    try {
      const strategy = this.strategies[symbol];
      if (!strategy) {
        return {
          symbol: symbol,
          action: 'HOLD',
          reason: 'No strategy configured',
          confidence: 0,
          timestamp: new Date()
        };
      }

      // Get historical data for analysis
      const historicalData = await this.getHistoricalDataForAnalysis(symbol);
      if (historicalData.length < 20) {
        return {
          symbol: symbol,
          action: 'HOLD',
          reason: 'Insufficient historical data',
          confidence: 0,
          timestamp: new Date()
        };
      }

      // Calculate technical indicators
      const indicators = this.calculateIndicators(historicalData);
      
      // Execute strategy logic
      const result = this.executePineScriptLogic(strategy, indicators, {
        price: historicalData[historicalData.length - 1].close
      });

      return {
        symbol: symbol,
        action: result.action,
        reason: result.reason,
        confidence: result.confidence,
        price: historicalData[historicalData.length - 1].close,
        timestamp: new Date()
      };

    } catch (error) {
      this.logger.error(`Error evaluating strategy for ${symbol}:`, error);
      return {
        symbol: symbol,
        action: 'HOLD',
        reason: 'Strategy evaluation error',
        confidence: 0,
        timestamp: new Date()
      };
    }
  }

  async getHistoricalDataForAnalysis(symbol) {
    try {
      // Get historical data from database
      const data = await this.db.getHistoricalData(symbol, 100);
      
      if (data.length === 0) {
        // If no data in database, generate mock data
        return this.generateMockHistoricalData(symbol);
      }
      
      return data;
    } catch (error) {
      this.logger.error(`Error getting historical data for ${symbol}:`, error);
      return this.generateMockHistoricalData(symbol);
    }
  }

  generateMockHistoricalData(symbol) {
    const data = [];
    const basePrice = symbol === 'BTC' ? 120000 : 4000;
    
    for (let i = 0; i < 100; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (99 - i));
      
      const price = basePrice + (Math.random() - 0.5) * 1000;
      data.push({
        timestamp: date,
        open: price,
        high: price + Math.random() * 100,
        low: price - Math.random() * 100,
        close: price + (Math.random() - 0.5) * 50,
        volume: Math.random() * 1000000
      });
    }
    
    return data;
  }

  calculateIndicators(historicalData) {
    if (historicalData.length < 20) {
      return {};
    }
    
    const closes = historicalData.map(d => d.close);
    const highs = historicalData.map(d => d.high);
    const lows = historicalData.map(d => d.low);
    const volumes = historicalData.map(d => d.volume);
    
    const indicators = {};
    
    // Simple Moving Averages
    indicators.sma10 = technicalIndicators.SMA.calculate({ period: 10, values: closes });
    indicators.sma20 = technicalIndicators.SMA.calculate({ period: 20, values: closes });
    
    // Exponential Moving Averages
    indicators.ema12 = technicalIndicators.EMA.calculate({ period: 12, values: closes });
    indicators.ema26 = technicalIndicators.EMA.calculate({ period: 26, values: closes });
    
    // RSI
    indicators.rsi = technicalIndicators.RSI.calculate({ period: 14, values: closes });
    
    // MACD
    indicators.macd = technicalIndicators.MACD.calculate({
      fastPeriod: 12,
      slowPeriod: 26,
      signalPeriod: 9,
      values: closes
    });
    
    // Bollinger Bands
    indicators.bollinger = technicalIndicators.BollingerBands.calculate({
      period: 20,
      values: closes,
      stdDev: 2
    });
    
    return indicators;
  }

  executePineScriptLogic(strategy, indicators, marketData) {
    try {
      // Use custom Pine Script if available, otherwise fall back to default logic
      if (strategy && strategy.code) {
        return this.executeCustomPineScript(strategy.code, indicators, marketData);
      }
      
      // Default logic (fallback)
      const currentPrice = marketData.price;
      const sma10 = indicators.sma10 && indicators.sma10.length > 0 ? indicators.sma10[indicators.sma10.length - 1] : null;
      const sma20 = indicators.sma20 && indicators.sma20.length > 0 ? indicators.sma20[indicators.sma20.length - 1] : null;
      const rsi = indicators.rsi && indicators.rsi.length > 0 ? indicators.rsi[indicators.rsi.length - 1] : null;
      
      let action = 'HOLD';
      let reason = 'No clear signal';
      let confidence = 0;
      
      // Simple moving average crossover logic
      if (sma10 && sma20) {
        if (sma10 > sma20) {
          action = 'BUY';
          reason = 'Fast MA above Slow MA';
          confidence = 0.7;
        } else if (sma10 < sma20) {
          action = 'SELL';
          reason = 'Fast MA below Slow MA';
          confidence = 0.7;
        }
      }
      
      // RSI overbought/oversold conditions
      if (rsi) {
        if (rsi > 70 && action === 'BUY') {
          action = 'HOLD';
          reason = 'RSI overbought, avoiding buy';
          confidence = 0.8;
        } else if (rsi < 30 && action === 'SELL') {
          action = 'HOLD';
          reason = 'RSI oversold, avoiding sell';
          confidence = 0.8;
        }
      }
      
      return { action, reason, confidence };
      
    } catch (error) {
      this.logger.error('Error executing Pine Script logic:', error);
      return {
        action: 'HOLD',
        reason: 'Strategy execution error',
        confidence: 0
      };
    }
  }

  executeCustomPineScript(code, indicators, marketData) {
    try {
      // Parse and execute custom Pine Script code
      // This is a simplified Pine Script interpreter
      
      const currentPrice = marketData.price;
      const closes = this.historicalData[marketData.symbol]?.map(d => d.close) || [currentPrice];
      
      // Extract indicators from the code
      const hasSMA = code.toLowerCase().includes('sma');
      const hasRSI = code.toLowerCase().includes('rsi');
      const hasMACD = code.toLowerCase().includes('macd');
      const hasBollinger = code.toLowerCase().includes('bollinger');
      
      let action = 'HOLD';
      let reason = 'Custom strategy';
      let confidence = 0;
      
      // Execute based on indicators mentioned in the code
      if (hasSMA && indicators.sma10 && indicators.sma20) {
        const sma10 = indicators.sma10[indicators.sma10.length - 1];
        const sma20 = indicators.sma20[indicators.sma20.length - 1];
        const sma10Prev = indicators.sma10[indicators.sma10.length - 2];
        const sma20Prev = indicators.sma20[indicators.sma20.length - 2];
        
        // Check for crossover signals
        if (sma10 > sma20 && sma10Prev <= sma20Prev) {
          action = 'BUY';
          reason = 'Custom SMA Strategy: Fast MA crossed above Slow MA';
          confidence = 75;
        } else if (sma10 < sma20 && sma10Prev >= sma20Prev) {
          action = 'SELL';
          reason = 'Custom SMA Strategy: Fast MA crossed below Slow MA';
          confidence = 75;
        } else if (sma10 > sma20) {
          action = 'BUY';
          reason = 'Custom SMA Strategy: Fast MA above Slow MA';
          confidence = 60;
        } else if (sma10 < sma20) {
          action = 'SELL';
          reason = 'Custom SMA Strategy: Fast MA below Slow MA';
          confidence = 60;
        }
      }
      
      if (hasRSI && indicators.rsi) {
        const rsi = indicators.rsi[indicators.rsi.length - 1];
        
        if (rsi < 30) {
          action = 'BUY';
          reason = 'Custom RSI Strategy: Oversold condition';
          confidence = 80;
        } else if (rsi > 70) {
          action = 'SELL';
          reason = 'Custom RSI Strategy: Overbought condition';
          confidence = 80;
        }
      }
      
      if (hasMACD && indicators.macd) {
        const macd = indicators.macd[indicators.macd.length - 1];
        const macdPrev = indicators.macd[indicators.macd.length - 2];
        
        if (macd.MACD > macd.signal && macdPrev.MACD <= macdPrev.signal) {
          action = 'BUY';
          reason = 'Custom MACD Strategy: MACD crossed above signal';
          confidence = 75;
        } else if (macd.MACD < macd.signal && macdPrev.MACD >= macdPrev.signal) {
          action = 'SELL';
          reason = 'Custom MACD Strategy: MACD crossed below signal';
          confidence = 75;
        } else if (macd.MACD > macd.signal) {
          action = 'BUY';
          reason = 'Custom MACD Strategy: MACD above signal';
          confidence = 60;
        } else if (macd.MACD < macd.signal) {
          action = 'SELL';
          reason = 'Custom MACD Strategy: MACD below signal';
          confidence = 60;
        }
      }
      
      if (hasBollinger && indicators.bollinger) {
        const bb = indicators.bollinger[indicators.bollinger.length - 1];
        
        if (currentPrice < bb.lower) {
          action = 'BUY';
          reason = 'Custom Bollinger Strategy: Price below lower band';
          confidence = 70;
        } else if (currentPrice > bb.upper) {
          action = 'SELL';
          reason = 'Custom Bollinger Strategy: Price above upper band';
          confidence = 70;
        }
      }
      
      this.logger.info(`Custom Pine Script executed: ${action} - ${reason}`);
      
      return { action, reason, confidence };
      
    } catch (error) {
      this.logger.error('Error executing custom Pine Script:', error);
      return {
        action: 'HOLD',
        reason: 'Custom strategy execution error',
        confidence: 0
      };
    }
  }

  combineDecisions(decisions) {
    // Combine multiple symbol decisions into overall action
    const actions = Object.values(decisions);
    
    if (actions.length === 0) {
      return {
        action: 'HOLD',
        reason: 'No decisions available',
        timestamp: new Date(),
        confidence: 0
      };
    }
    
    // Count actions
    const actionCounts = actions.reduce((acc, decision) => {
      acc[decision.action] = (acc[decision.action] || 0) + 1;
      return acc;
    }, {});
    
    // Find most common action
    const mostCommonAction = Object.keys(actionCounts).reduce((a, b) => 
      actionCounts[a] > actionCounts[b] ? a : b
    );
    
    // Calculate average confidence
    const avgConfidence = actions.reduce((sum, decision) => sum + decision.confidence, 0) / actions.length;
    
    return {
      action: mostCommonAction,
      reason: `Combined decision from ${actions.length} symbols`,
      timestamp: new Date(),
      confidence: avgConfidence,
      details: decisions
    };
  }

  async getStrategy(symbol) {
    return this.strategies[symbol] || null;
  }

  async getAllStrategies() {
    return this.strategies;
  }

  async updateHistoricalData(symbol, data) {
    this.historicalData[symbol] = data;
  }
}

module.exports = LogicEngine;
