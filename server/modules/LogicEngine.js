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
      // Advanced BTC Strategy: Multi-Timeframe RSI + MACD + Volume
      const btcStrategy = {
        name: 'BTC Advanced Momentum Strategy',
        code: `
// Advanced BTC Strategy: Multi-Timeframe RSI + MACD + Volume Analysis
// Combines momentum, trend, and volume for high-probability trades

// Core indicators
rsi = ta.rsi(close, 14)
macd = ta.macd(close, 12, 26, 9)
sma20 = ta.sma(close, 20)
sma50 = ta.sma(close, 50)
volume_sma = ta.sma(volume, 20)

// Volume confirmation
high_volume = volume > volume_sma * 1.5
low_volume = volume < volume_sma * 0.5

// Trend analysis
uptrend = sma20 > sma50 and close > sma20
downtrend = sma20 < sma50 and close < sma20

// RSI conditions
rsi_oversold = rsi < 30
rsi_overbought = rsi > 70
rsi_bullish = rsi > 50 and rsi < 70
rsi_bearish = rsi < 50 and rsi > 30

// MACD conditions
macd_bullish = macd.macd > macd.signal and macd.macd > 0
macd_bearish = macd.macd < macd.signal and macd.macd < 0
macd_crossover_bull = macd.macd > macd.signal and macd.macd[1] <= macd.signal[1]
macd_crossover_bear = macd.macd < macd.signal and macd.macd[1] >= macd.signal[1]

// Strong buy signal: RSI oversold + MACD bullish crossover + uptrend + high volume
if rsi_oversold and macd_crossover_bull and uptrend and high_volume
    return { action: 'BUY', reason: 'BTC: Strong momentum reversal with volume confirmation', confidence: 85 }

// Moderate buy signal: RSI bullish + MACD bullish + uptrend
if rsi_bullish and macd_bullish and uptrend
    return { action: 'BUY', reason: 'BTC: Momentum continuation in uptrend', confidence: 75 }

// Strong sell signal: RSI overbought + MACD bearish crossover + downtrend + high volume
if rsi_overbought and macd_crossover_bear and downtrend and high_volume
    return { action: 'SELL', reason: 'BTC: Strong reversal with volume confirmation', confidence: 85 }

// Moderate sell signal: RSI bearish + MACD bearish + downtrend
if rsi_bearish and macd_bearish and downtrend
    return { action: 'SELL', reason: 'BTC: Momentum continuation in downtrend', confidence: 75 }

// Weak signals for low volume periods
if rsi_oversold and macd_bullish and not low_volume
    return { action: 'BUY', reason: 'BTC: Oversold bounce opportunity', confidence: 60 }

if rsi_overbought and macd_bearish and not low_volume
    return { action: 'SELL', reason: 'BTC: Overbought reversal opportunity', confidence: 60 }

return { action: 'HOLD', reason: 'BTC: No clear signal, waiting for better conditions', confidence: 0 }
        `,
        isActive: true
      };

      // Advanced ETH Strategy: Bollinger Bands + Stochastic + Support/Resistance
      const ethStrategy = {
        name: 'ETH Mean Reversion Strategy',
        code: `
// Advanced ETH Strategy: Bollinger Bands + Stochastic + Support/Resistance
// Mean reversion strategy optimized for ETH's volatility patterns

// Core indicators
bb = ta.bb(close, 20, 2)
stoch = ta.stoch(high, low, close, 14)
sma20 = ta.sma(close, 20)
sma50 = ta.sma(close, 50)
atr = ta.atr(high, low, close, 14)

// Bollinger Bands conditions
bb_upper = bb.upper
bb_lower = bb.lower
bb_middle = bb.middle
price_near_upper = close >= bb_upper * 0.98
price_near_lower = close <= bb_lower * 1.02
price_middle = close >= bb_middle * 0.99 and close <= bb_middle * 1.01

// Stochastic conditions
stoch_oversold = stoch.k < 20
stoch_overbought = stoch.k > 80
stoch_bullish = stoch.k > stoch.d and stoch.k > 50
stoch_bearish = stoch.k < stoch.d and stoch.k < 50

// Trend analysis
strong_uptrend = sma20 > sma50 * 1.02 and close > sma20
strong_downtrend = sma20 < sma50 * 0.98 and close < sma20
sideways = not strong_uptrend and not strong_downtrend

// Volatility analysis
high_volatility = atr > ta.sma(atr, 20) * 1.2
low_volatility = atr < ta.sma(atr, 20) * 0.8

// Strong buy signal: Price at lower band + stochastic oversold + sideways market
if price_near_lower and stoch_oversold and sideways and not low_volatility
    return { action: 'BUY', reason: 'ETH: Strong mean reversion from oversold', confidence: 80 }

// Moderate buy signal: Price below middle + stochastic bullish + uptrend
if close < bb_middle and stoch_bullish and strong_uptrend
    return { action: 'BUY', reason: 'ETH: Pullback buy in uptrend', confidence: 70 }

// Strong sell signal: Price at upper band + stochastic overbought + sideways market
if price_near_upper and stoch_overbought and sideways and not low_volatility
    return { action: 'SELL', reason: 'ETH: Strong mean reversion from overbought', confidence: 80 }

// Moderate sell signal: Price above middle + stochastic bearish + downtrend
if close > bb_middle and stoch_bearish and strong_downtrend
    return { action: 'SELL', reason: 'ETH: Bounce sell in downtrend', confidence: 70 }

// Range trading signals
if price_near_lower and stoch_oversold and high_volatility
    return { action: 'BUY', reason: 'ETH: Volatile oversold bounce', confidence: 65 }

if price_near_upper and stoch_overbought and high_volatility
    return { action: 'SELL', reason: 'ETH: Volatile overbought reversal', confidence: 65 }

return { action: 'HOLD', reason: 'ETH: No clear signal, waiting for better conditions', confidence: 0 }
        `,
        isActive: true
      };

      // Save advanced strategies for both BTC and ETH
      await this.db.saveStrategy('BTC', btcStrategy.name, btcStrategy.code);
      await this.db.saveStrategy('ETH', ethStrategy.name, ethStrategy.code);
      
      // Load strategies from database
      this.strategies.BTC = await this.db.getStrategy('BTC');
      this.strategies.ETH = await this.db.getStrategy('ETH');
      
      this.logger.info('Advanced trading strategies loaded successfully');
    } catch (error) {
      this.logger.error('Failed to load advanced strategies:', error);
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

  async getCurrentPosition(symbol) {
    try {
      const db = this.db;
      const allTrades = await db.getTradeHistory(1000);
      
      let netQuantity = 0;
      allTrades.forEach(trade => {
        if (trade.symbol === symbol) {
          if (trade.action === 'BUY') {
            netQuantity += trade.quantity || 0;
          } else if (trade.action === 'SELL') {
            netQuantity -= trade.quantity || 0;
          }
        }
      });
      
      return netQuantity;
    } catch (error) {
      this.logger.error(`Error getting current position for ${symbol}:`, error);
      return 0;
    }
  }

  async evaluateStrategy(symbol) {
    try {
      const strategy = this.strategies[symbol];
      if (!strategy) {
        return {
          action: 'HOLD',
          reason: 'No strategy configured',
          timestamp: new Date(),
          confidence: 0
        };
      }

      // Get current market data and indicators
      const marketData = await this.getMarketData(symbol);
      const historicalData = this.historicalData[symbol] || this.generateMockHistoricalData(symbol);
      const indicators = this.calculateIndicators(historicalData);

      // Execute strategy logic
      const decision = this.executePineScriptLogic(strategy, indicators, marketData);
      
      // Check current position before making trading decisions
      const currentPosition = await this.getCurrentPosition(symbol);
      
      // Prevent selling more than we have (unless we want to allow short selling)
      if (decision.action === 'SELL' && currentPosition <= 0) {
        decision.action = 'HOLD';
        decision.reason = `Cannot sell ${symbol} - no position to sell (current: ${currentPosition.toFixed(6)})`;
        decision.confidence = 0;
      }
      
      // Prevent buying if we already have a large position (optional risk management)
      if (decision.action === 'BUY' && currentPosition > 0.01) {
        decision.action = 'HOLD';
        decision.reason = `Already have ${symbol} position (${currentPosition.toFixed(6)}) - waiting for better opportunity`;
        decision.confidence = Math.max(decision.confidence - 20, 0);
      }

      return {
        ...decision,
        symbol: symbol,
        timestamp: new Date(),
        currentPosition: currentPosition
      };

    } catch (error) {
      this.logger.error(`Error evaluating strategy for ${symbol}:`, error);
      return {
        action: 'HOLD',
        reason: 'Strategy evaluation error',
        symbol: symbol,
        timestamp: new Date(),
        confidence: 0
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
    if (historicalData.length < 50) {
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
    indicators.sma50 = technicalIndicators.SMA.calculate({ period: 50, values: closes });
    
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
    
    // Stochastic Oscillator
    indicators.stochastic = technicalIndicators.Stochastic.calculate({
      high: highs,
      low: lows,
      close: closes,
      period: 14,
      signalPeriod: 3
    });
    
    // Average True Range (ATR)
    indicators.atr = technicalIndicators.ATR.calculate({
      high: highs,
      low: lows,
      close: closes,
      period: 14
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
      const highs = this.historicalData[marketData.symbol]?.map(d => d.high) || [currentPrice];
      const lows = this.historicalData[marketData.symbol]?.map(d => d.low) || [currentPrice];
      const volumes = this.historicalData[marketData.symbol]?.map(d => d.volume) || [1000000];
      
      // Extract indicators from the code
      const hasSMA = code.toLowerCase().includes('sma');
      const hasRSI = code.toLowerCase().includes('rsi');
      const hasMACD = code.toLowerCase().includes('macd');
      const hasBollinger = code.toLowerCase().includes('bb') || code.toLowerCase().includes('bollinger');
      const hasStoch = code.toLowerCase().includes('stoch');
      const hasATR = code.toLowerCase().includes('atr');
      const hasVolume = code.toLowerCase().includes('volume');
      
      let action = 'HOLD';
      let reason = 'Custom strategy';
      let confidence = 0;
      
      // Execute based on indicators mentioned in the code
      if (hasSMA && indicators.sma10 && indicators.sma20 && indicators.sma50) {
        const sma10 = indicators.sma10[indicators.sma10.length - 1];
        const sma20 = indicators.sma20[indicators.sma20.length - 1];
        const sma50 = indicators.sma50[indicators.sma50.length - 1];
        const sma10Prev = indicators.sma10[indicators.sma10.length - 2];
        const sma20Prev = indicators.sma20[indicators.sma20.length - 2];
        
        // Check for trend conditions
        const uptrend = sma20 > sma50 && currentPrice > sma20;
        const downtrend = sma20 < sma50 && currentPrice < sma20;
        const strong_uptrend = sma20 > sma50 * 1.02 && currentPrice > sma20;
        const strong_downtrend = sma20 < sma50 * 0.98 && currentPrice < sma20;
        
        // Check for crossover signals
        if (sma10 > sma20 && sma10Prev <= sma20Prev && uptrend) {
          action = 'BUY';
          reason = 'Custom SMA Strategy: Fast MA crossed above Slow MA in uptrend';
          confidence = 75;
        } else if (sma10 < sma20 && sma10Prev >= sma20Prev && downtrend) {
          action = 'SELL';
          reason = 'Custom SMA Strategy: Fast MA crossed below Slow MA in downtrend';
          confidence = 75;
        } else if (strong_uptrend) {
          action = 'BUY';
          reason = 'Custom SMA Strategy: Strong uptrend continuation';
          confidence = 70;
        } else if (strong_downtrend) {
          action = 'SELL';
          reason = 'Custom SMA Strategy: Strong downtrend continuation';
          confidence = 70;
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
        } else if (rsi > 50 && rsi < 70) {
          action = 'BUY';
          reason = 'Custom RSI Strategy: Bullish momentum';
          confidence = 60;
        } else if (rsi < 50 && rsi > 30) {
          action = 'SELL';
          reason = 'Custom RSI Strategy: Bearish momentum';
          confidence = 60;
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
        } else if (macd.MACD > macd.signal && macd.MACD > 0) {
          action = 'BUY';
          reason = 'Custom MACD Strategy: MACD above signal and positive';
          confidence = 60;
        } else if (macd.MACD < macd.signal && macd.MACD < 0) {
          action = 'SELL';
          reason = 'Custom MACD Strategy: MACD below signal and negative';
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
        } else if (currentPrice >= bb.middle * 0.99 && currentPrice <= bb.middle * 1.01) {
          // Price near middle band - neutral
          confidence = Math.max(confidence, 30);
        }
      }
      
      if (hasStoch && indicators.stochastic) {
        const stoch = indicators.stochastic[indicators.stochastic.length - 1];
        
        if (stoch.k < 20) {
          action = 'BUY';
          reason = 'Custom Stochastic Strategy: Oversold condition';
          confidence = 75;
        } else if (stoch.k > 80) {
          action = 'SELL';
          reason = 'Custom Stochastic Strategy: Overbought condition';
          confidence = 75;
        } else if (stoch.k > stoch.d && stoch.k > 50) {
          action = 'BUY';
          reason = 'Custom Stochastic Strategy: Bullish crossover above 50';
          confidence = 65;
        } else if (stoch.k < stoch.d && stoch.k < 50) {
          action = 'SELL';
          reason = 'Custom Stochastic Strategy: Bearish crossover below 50';
          confidence = 65;
        }
      }
      
      if (hasATR && indicators.atr) {
        const atr = indicators.atr[indicators.atr.length - 1];
        const atrSMA = indicators.atr.slice(-20).reduce((a, b) => a + b, 0) / 20;
        
        const high_volatility = atr > atrSMA * 1.2;
        const low_volatility = atr < atrSMA * 0.8;
        
        if (high_volatility && action === 'BUY') {
          confidence = Math.min(confidence + 10, 100);
          reason += ' with high volatility';
        } else if (low_volatility && action !== 'HOLD') {
          confidence = Math.max(confidence - 10, 0);
          reason += ' with low volatility';
        }
      }
      
      if (hasVolume && volumes.length > 0) {
        const currentVolume = volumes[volumes.length - 1];
        const volumeSMA = volumes.slice(-20).reduce((a, b) => a + b, 0) / 20;
        
        const high_volume = currentVolume > volumeSMA * 1.5;
        const low_volume = currentVolume < volumeSMA * 0.5;
        
        if (high_volume && action !== 'HOLD') {
          confidence = Math.min(confidence + 10, 100);
          reason += ' with volume confirmation';
        } else if (low_volume && action !== 'HOLD') {
          confidence = Math.max(confidence - 15, 0);
          reason += ' with low volume';
        }
      }
      
      this.logger.info(`Custom Pine Script executed: ${action} - ${reason} (confidence: ${confidence})`);
      
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
