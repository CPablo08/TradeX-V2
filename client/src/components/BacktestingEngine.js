import React, { useState, useEffect } from 'react';
import './BacktestingEngine.css';

const BacktestingEngine = ({ strategy, symbol, onResults }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [backtestParams, setBacktestParams] = useState({
    startDate: '2024-01-01',
    endDate: new Date().toISOString().split('T')[0],
    initialCapital: 10000,
    positionSize: 0.1, // 10% of capital per trade
    commission: 0.001, // 0.1% commission
    slippage: 0.0005 // 0.05% slippage
  });

  // Simulate historical data generation
  const generateHistoricalData = (startDate, endDate) => {
    const data = [];
    const start = new Date(startDate);
    const end = new Date(endDate);
    const basePrice = symbol === 'BTC' ? 45000 : 3000;
    
    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
      const volatility = 0.02; // 2% daily volatility
      const randomChange = (Math.random() - 0.5) * volatility;
      const price = basePrice * (1 + randomChange);
      
      data.push({
        date: new Date(date),
        open: price * (1 + (Math.random() - 0.5) * 0.01),
        high: price * (1 + Math.random() * 0.02),
        low: price * (1 - Math.random() * 0.02),
        close: price,
        volume: Math.floor(Math.random() * 1000000) + 100000
      });
      
      basePrice = price;
    }
    
    return data;
  };

  // Simple Pine Script interpreter
  const interpretPineScript = (script, data, index) => {
    try {
      // Basic Pine Script interpretation
      const context = {
        close: data[index]?.close || 0,
        open: data[index]?.open || 0,
        high: data[index]?.high || 0,
        low: data[index]?.low || 0,
        volume: data[index]?.volume || 0,
        index: index
      };

      // Extract return statement from script
      const returnMatch = script.match(/return\s*\{([^}]+)\}/);
      if (!returnMatch) {
        return { action: 'HOLD', confidence: 0, reason: 'No return statement found' };
      }

      const returnContent = returnMatch[1];
      
      // Parse action
      const actionMatch = returnContent.match(/action:\s*["']([^"']+)["']/);
      const action = actionMatch ? actionMatch[1] : 'HOLD';
      
      // Parse confidence
      const confidenceMatch = returnContent.match(/confidence:\s*(\d+)/);
      const confidence = confidenceMatch ? parseInt(confidenceMatch[1]) : 0;
      
      // Parse reason
      const reasonMatch = returnContent.match(/reason:\s*["']([^"']+)["']/);
      const reason = reasonMatch ? reasonMatch[1] : 'No reason provided';

      return { action, confidence, reason };
    } catch (error) {
      return { action: 'HOLD', confidence: 0, reason: 'Script interpretation error' };
    }
  };

  // Run backtest
  const runBacktest = async () => {
    if (!strategy.trim()) {
      alert('Please enter a strategy first');
      return;
    }

    setIsRunning(true);
    setProgress(0);
    setResults(null);

    try {
      // Generate historical data
      const data = generateHistoricalData(backtestParams.startDate, backtestParams.endDate);
      setHistoricalData(data);

      // Initialize backtest variables
      let capital = backtestParams.initialCapital;
      let position = 0;
      let trades = [];
      let equity = [capital];
      let maxDrawdown = 0;
      let peak = capital;

      // Run simulation
      for (let i = 0; i < data.length; i++) {
        const signal = interpretPineScript(strategy, data, i);
        const currentPrice = data[i].close;
        
        // Execute trades based on signal
        if (signal.action === 'BUY' && signal.confidence > 50 && position === 0) {
          const tradeSize = capital * backtestParams.positionSize;
          const shares = tradeSize / currentPrice;
          const cost = shares * currentPrice * (1 + backtestParams.commission + backtestParams.slippage);
          
          if (cost <= capital) {
            position = shares;
            capital -= cost;
            
            trades.push({
              date: data[i].date,
              action: 'BUY',
              price: currentPrice,
              shares: shares,
              value: cost,
              confidence: signal.confidence,
              reason: signal.reason
            });
          }
        } else if (signal.action === 'SELL' && signal.confidence > 50 && position > 0) {
          const proceeds = position * currentPrice * (1 - backtestParams.commission - backtestParams.slippage);
          capital += proceeds;
          
          trades.push({
            date: data[i].date,
            action: 'SELL',
            price: currentPrice,
            shares: position,
            value: proceeds,
            confidence: signal.confidence,
            reason: signal.reason
          });
          
          position = 0;
        }

        // Calculate current equity
        const currentEquity = capital + (position * currentPrice);
        equity.push(currentEquity);

        // Calculate drawdown
        if (currentEquity > peak) {
          peak = currentEquity;
        }
        const drawdown = (peak - currentEquity) / peak;
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown;
        }

        // Update progress
        setProgress(((i + 1) / data.length) * 100);
        
        // Small delay to show progress
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      // Close any remaining position
      if (position > 0) {
        const finalPrice = data[data.length - 1].close;
        const proceeds = position * finalPrice * (1 - backtestParams.commission - backtestParams.slippage);
        capital += proceeds;
        
        trades.push({
          date: data[data.length - 1].date,
          action: 'SELL',
          price: finalPrice,
          shares: position,
          value: proceeds,
          confidence: 100,
          reason: 'Backtest completion'
        });
      }

      // Calculate final results
      const finalEquity = capital;
      const totalReturn = ((finalEquity - backtestParams.initialCapital) / backtestParams.initialCapital) * 100;
      const winningTrades = trades.filter(t => t.action === 'SELL' && t.value > t.shares * trades.find(bt => bt.date < t.date && bt.action === 'BUY')?.price).length;
      const totalTrades = trades.filter(t => t.action === 'SELL').length;
      const winRate = totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0;

      const backtestResults = {
        initialCapital: backtestParams.initialCapital,
        finalEquity: finalEquity,
        totalReturn: totalReturn,
        maxDrawdown: maxDrawdown * 100,
        totalTrades: totalTrades,
        winningTrades: winningTrades,
        winRate: winRate,
        trades: trades,
        equity: equity,
        data: data
      };

      setResults(backtestResults);
      if (onResults) {
        onResults(backtestResults);
      }

    } catch (error) {
      console.error('Backtest error:', error);
      alert('Error running backtest: ' + error.message);
    } finally {
      setIsRunning(false);
      setProgress(0);
    }
  };

  return (
    <div className="backtesting-engine">
      <div className="backtest-header">
        <h3>Backtesting Engine</h3>
        <div className="backtest-controls">
          <div className="param-group">
            <label>Start Date:</label>
            <input
              type="date"
              value={backtestParams.startDate}
              onChange={(e) => setBacktestParams({...backtestParams, startDate: e.target.value})}
            />
          </div>
          <div className="param-group">
            <label>End Date:</label>
            <input
              type="date"
              value={backtestParams.endDate}
              onChange={(e) => setBacktestParams({...backtestParams, endDate: e.target.value})}
            />
          </div>
          <div className="param-group">
            <label>Initial Capital:</label>
            <input
              type="number"
              value={backtestParams.initialCapital}
              onChange={(e) => setBacktestParams({...backtestParams, initialCapital: parseFloat(e.target.value)})}
            />
          </div>
          <div className="param-group">
            <label>Position Size (%):</label>
            <input
              type="number"
              step="0.01"
              value={backtestParams.positionSize * 100}
              onChange={(e) => setBacktestParams({...backtestParams, positionSize: parseFloat(e.target.value) / 100})}
            />
          </div>
          <button 
            className={`run-backtest-btn ${isRunning ? 'running' : ''}`}
            onClick={runBacktest}
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Run Backtest'}
          </button>
        </div>
      </div>

      {isRunning && (
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{width: `${progress}%`}}></div>
          </div>
          <div className="progress-text">{Math.round(progress)}%</div>
        </div>
      )}

      {results && (
        <div className="backtest-results">
          <div className="results-grid">
            <div className="result-card">
              <div className="result-label">Total Return</div>
              <div className={`result-value ${results.totalReturn >= 0 ? 'positive' : 'negative'}`}>
                {results.totalReturn.toFixed(2)}%
              </div>
            </div>
            <div className="result-card">
              <div className="result-label">Final Equity</div>
              <div className="result-value">
                ${results.finalEquity.toLocaleString()}
              </div>
            </div>
            <div className="result-card">
              <div className="result-label">Max Drawdown</div>
              <div className="result-value negative">
                {results.maxDrawdown.toFixed(2)}%
              </div>
            </div>
            <div className="result-card">
              <div className="result-label">Total Trades</div>
              <div className="result-value">
                {results.totalTrades}
              </div>
            </div>
            <div className="result-card">
              <div className="result-label">Win Rate</div>
              <div className="result-value">
                {results.winRate.toFixed(1)}%
              </div>
            </div>
            <div className="result-card">
              <div className="result-label">Winning Trades</div>
              <div className="result-value">
                {results.winningTrades}
              </div>
            </div>
          </div>

          <div className="trades-list">
            <h4>Trade History</h4>
            <div className="trades-container">
              {results.trades.map((trade, index) => (
                <div key={index} className={`trade-item ${trade.action.toLowerCase()}`}>
                  <div className="trade-date">{trade.date.toLocaleDateString()}</div>
                  <div className="trade-action">{trade.action}</div>
                  <div className="trade-price">${trade.price.toFixed(2)}</div>
                  <div className="trade-shares">{trade.shares.toFixed(4)}</div>
                  <div className="trade-value">${trade.value.toFixed(2)}</div>
                  <div className="trade-confidence">{trade.confidence}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BacktestingEngine;
