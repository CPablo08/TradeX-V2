import React, { useState, useEffect } from 'react';
import './App.css';
import TradingViewWidget from './components/TradingViewWidget';

function App() {
  const [lastUpdated, setLastUpdated] = useState('');
  const [systemStatus, setSystemStatus] = useState('offline');
  const [portfolioData, setPortfolioData] = useState({
    totalPL: 0,
    totalTrades: 0,
    portfolioValue: 0
  });
  const [totalAssets, setTotalAssets] = useState({
    btcValue: 0,
    ethValue: 0,
    totalValue: 0
  });

  const [showConfig, setShowConfig] = useState(false);
  const [tradingMode, setTradingMode] = useState('paper');
  const [tradingLogs, setTradingLogs] = useState([]);
  const [isTradingActive, setIsTradingActive] = useState(false);
  const [tradingStatus, setTradingStatus] = useState('');
  const [btcStrategy, setBtcStrategy] = useState('');
  const [ethStrategy, setEthStrategy] = useState('');
  const [strategyStatus, setStrategyStatus] = useState('');
  const [tradesHistory, setTradesHistory] = useState([]);

  useEffect(() => {
    updateTimestamp();
    fetchSystemStatus();
    fetchPortfolioData();
    fetchTotalAssets();
    fetchTradingLogs();
    fetchTradingStatus();
    fetchStrategies();
    fetchTradesHistory();
    
    const timestampInterval = setInterval(updateTimestamp, 1000);
    const statusInterval = setInterval(fetchSystemStatus, 10000);
    const dataInterval = setInterval(fetchPortfolioData, 3000);
    const assetsInterval = setInterval(fetchTotalAssets, 3000);
    const logsInterval = setInterval(fetchTradingLogs, 3000);
    const tradingStatusInterval = setInterval(fetchTradingStatus, 3000);
    const tradesInterval = setInterval(fetchTradesHistory, 3000);
    
    return () => {
      clearInterval(timestampInterval);
      clearInterval(statusInterval);
      clearInterval(dataInterval);
      clearInterval(assetsInterval);
      clearInterval(logsInterval);
      clearInterval(tradingStatusInterval);
      clearInterval(tradesInterval);
    };
  }, []);

  const updateTimestamp = () => {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    setLastUpdated(`Last updated: ${timeString}`);
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/status');
      if (response.ok) {
        setSystemStatus('online');
      } else {
        setSystemStatus('offline');
      }
    } catch (error) {
      console.error('Error checking system status:', error);
      setSystemStatus('offline');
    }
  };

  const fetchPortfolioData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/data/portfolio-metrics');
      if (response.ok) {
        const data = await response.json();
        console.log('Portfolio data received:', data.data);
        setPortfolioData({
          totalPL: data.data?.totalPL || 0,
          totalTrades: data.data?.totalTrades || 0,
          portfolioValue: data.data?.portfolioValue || 1000
        });
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    }
  };

  const fetchTotalAssets = async () => {
    try {
      const [btcResponse, ethResponse] = await Promise.all([
        fetch('https://api.coinbase.com/v2/prices/BTC-USD/spot'),
        fetch('https://api.coinbase.com/v2/prices/ETH-USD/spot')
      ]);
      
      if (btcResponse.ok && ethResponse.ok) {
        const btcData = await btcResponse.json();
        const ethData = await ethResponse.json();
        
        const btcPrice = parseFloat(btcData.data.amount);
        const ethPrice = parseFloat(ethData.data.amount);
        
        // Calculate total assets based on recent trades
        const response = await fetch('http://localhost:5000/api/trading/history?limit=100');
        if (response.ok) {
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
          
          const btcValue = btcQuantity * btcPrice;
          const ethValue = ethQuantity * ethPrice;
          const totalValue = btcValue + ethValue;
          
          console.log('Total assets calculation:', {
            btcQuantity,
            ethQuantity,
            btcPrice,
            ethPrice,
            btcValue,
            ethValue,
            totalValue
          });
          
          setTotalAssets({
            btcValue: btcValue,
            ethValue: ethValue,
            totalValue: totalValue
          });
        }
      }
    } catch (error) {
      console.error('Error fetching total assets:', error);
    }
  };

  const fetchTradingLogs = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/trading-logs');
      if (response.ok) {
        const data = await response.json();
        setTradingLogs(data.slice(-50)); // Keep last 50 entries
      }
    } catch (error) {
      console.error('Error fetching trading logs:', error);
    }
  };

  const fetchTradingStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/trading-status');
      if (response.ok) {
        const data = await response.json();
        setIsTradingActive(data.isActive);
        setTradingMode(data.mode);
      }
    } catch (error) {
      console.error('Error fetching trading status:', error);
    }
  };

  const fetchStrategies = async () => {
    try {
      const [btcResponse, ethResponse] = await Promise.all([
        fetch('http://localhost:5000/api/strategies/BTC'),
        fetch('http://localhost:5000/api/strategies/ETH')
      ]);
      
      if (btcResponse.ok) {
        const btcData = await btcResponse.json();
        setBtcStrategy(btcData.data?.code || '');
      }
      
      if (ethResponse.ok) {
        const ethData = await ethResponse.json();
        setEthStrategy(ethData.data?.code || '');
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  };

  const updateStrategy = async (symbol, code) => {
    try {
      setStrategyStatus('Updating strategy...');
      
      const response = await fetch(`http://localhost:5000/api/strategies/${symbol}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: `${symbol} Strategy`,
          code: code
        })
      });

      if (response.ok) {
        setStrategyStatus(`✅ ${symbol} strategy updated successfully!`);
        setTimeout(() => setStrategyStatus(''), 3000);
      } else {
        const errorData = await response.json();
        setStrategyStatus(`❌ Failed to update ${symbol} strategy: ${errorData.error || 'Unknown error'}`);
        setTimeout(() => setStrategyStatus(''), 5000);
      }
    } catch (error) {
      console.error('Error updating strategy:', error);
      setStrategyStatus(`❌ Error updating ${symbol} strategy: ${error.message}`);
      setTimeout(() => setStrategyStatus(''), 5000);
    }
  };

  const fetchTradesHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/trading/history');
      if (response.ok) {
        const result = await response.json();
        // The API returns { success: true, data: [...] }
        const trades = result.success ? result.data : [];
        console.log('Fetched trades:', trades.length, 'trades');
        setTradesHistory(trades.slice(-50)); // Keep last 50 trades
      }
    } catch (error) {
      console.error('Error fetching trades history:', error);
    }
  };

  const toggleTradingMode = async () => {
    const newMode = tradingMode === 'paper' ? 'real' : 'paper';
    setTradingMode(newMode);
    
    try {
      // Send trading mode change to backend
      await fetch('http://localhost:5000/api/system/trading-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mode: newMode })
      });
    } catch (error) {
      console.error('Error updating trading mode:', error);
    }
  };

  const startTrading = async () => {
    try {
      setTradingStatus('Starting trading system...');
      
      // Send start trading command to backend
      const response = await fetch('http://localhost:5000/api/system/start-trading', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          mode: tradingMode,
          action: 'start'
        })
      });

      if (response.ok) {
        setIsTradingActive(true);
        setTradingStatus('✅ Trading system is now active and making decisions!');
        
        // Immediately refresh data after starting
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
        
        // Clear status after 5 seconds
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      } else {
        setTradingStatus('❌ Failed to start trading system');
      }
    } catch (error) {
      console.error('Error starting trading:', error);
      setTradingStatus('❌ Error starting trading system');
    }
  };

  const stopTrading = async () => {
    try {
      setTradingStatus('Stopping trading system...');
      
      const response = await fetch('http://localhost:5000/api/system/start-trading', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          mode: tradingMode,
          action: 'stop'
        })
      });

      if (response.ok) {
        setIsTradingActive(false);
        setTradingStatus('⏹️ Trading system stopped');
        
        // Immediately refresh data after stopping
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
        
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      } else {
        setTradingStatus('❌ Failed to stop trading system');
      }
    } catch (error) {
      console.error('Error stopping trading:', error);
      setTradingStatus('❌ Error stopping trading system');
    }
  };

  const restartTradingSession = async () => {
    try {
      setTradingStatus('Restarting trading session...');
      
      const response = await fetch('http://localhost:5000/api/system/restart-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        // Refresh all data after restart
        fetchPortfolioData();
        fetchTradesHistory();
        fetchTradingLogs();
        setTradingStatus('🔄 Trading session restarted successfully!');
        setTimeout(() => setTradingStatus(''), 5000);
      } else {
        setTradingStatus('❌ Failed to restart trading session');
      }
    } catch (error) {
      console.error('Error restarting trading session:', error);
      setTradingStatus('❌ Error restarting trading session');
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  const getStatusDisplay = () => {
    if (systemStatus === 'online') {
      return (
        <span className="status-indicator online">
          Status: <span className="status-text online">Online</span>
        </span>
      );
    } else {
      return (
        <span className="status-indicator offline">
          Status: <span className="status-text offline">Offline</span>
        </span>
      );
    }
  };

  const formatLogTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const formatTradeTimestamp = (timestamp) => {
    // Handle both ISO string and database timestamp formats
    let date;
    if (typeof timestamp === 'string') {
      // If it's already an ISO string, use it directly
      if (timestamp.includes('T') && timestamp.includes('Z')) {
        date = new Date(timestamp);
      } else {
        // If it's a database timestamp like "2025-08-13 22:22:00", convert it
        date = new Date(timestamp.replace(' ', 'T') + 'Z');
      }
    } else {
      date = new Date(timestamp);
    }
    
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const formatTradeAmount = (quantity, price) => {
    const total = quantity * price;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(total);
  };

  return (
    <div className="App">
      {/* Trading Configuration Button */}
      <button 
        className="config-button"
        onClick={() => setShowConfig(true)}
      >
        Trading Configuration
      </button>

      {/* Top Section */}
      <div className="top-section">
        <div className="branding">
          <img src="/TradeX-Logo.png" alt="TradeX" className="logo" />
        </div>
        <div className="status-section">
          <span className="last-updated">{lastUpdated}</span>
          {getStatusDisplay()}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-title">Total P&L</div>
          <div className={`card-value ${portfolioData.totalPL >= 0 ? 'positive' : 'negative'}`}>
            {formatCurrency(portfolioData.totalPL)}
          </div>
          <div className="card-change">
            {portfolioData.totalPL >= 0 ? '+' : ''}{((portfolioData.totalPL / 1000) * 100).toFixed(1)}% from starting balance
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-title">Total Trades</div>
          <div className="card-value">{portfolioData.totalTrades}</div>
          <div className="card-change">
            {portfolioData.totalTrades > 0 ? 'Active trading session' : 'No trades yet'}
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-title">Portfolio Value</div>
          <div className="card-value">{formatCurrency(portfolioData.portfolioValue)}</div>
          <div className="card-change">
            Starting: $1,000 | Current: {formatCurrency(portfolioData.portfolioValue)}
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-title">Total Assets</div>
          <div className="card-value">{formatCurrency(totalAssets.totalValue)}</div>
          <div className="card-change">
            BTC: {formatCurrency(totalAssets.btcValue)} | ETH: {formatCurrency(totalAssets.ethValue)}
          </div>
        </div>
      </div>

      {/* Main Chart Section */}
      <div className="chart-section">
        <TradingViewWidget />
      </div>

      {/* Full Screen Configuration Panel */}
      {showConfig && (
        <div className="config-overlay">
          <div className="config-panel">
            <div className="config-header">
              <h2>Trading Configuration</h2>
              <button 
                className="close-button"
                onClick={() => setShowConfig(false)}
              >
                ×
              </button>
            </div>
            
            <div className="config-content">
              <div className="config-section">
                <h3>Trading Mode</h3>
                <div className="trading-mode-toggle">
                  <button 
                    className={`mode-btn ${tradingMode === 'paper' ? 'active' : ''}`}
                    onClick={() => tradingMode !== 'paper' && toggleTradingMode()}
                  >
                    Paper Trading
                  </button>
                  <button 
                    className={`mode-btn ${tradingMode === 'real' ? 'active' : ''}`}
                    onClick={() => tradingMode !== 'real' && toggleTradingMode()}
                  >
                    Real Trading
                  </button>
                </div>
                <p className="mode-description">
                  Current Mode: <strong>{tradingMode === 'paper' ? 'Paper Trading (Safe)' : 'Real Trading (Live Money)'}</strong>
                </p>
              </div>

              <div className="config-section">
                <h3>Trading Control</h3>
                <div className="trading-control">
                  {!isTradingActive ? (
                    <button 
                      className="start-trading-btn"
                      onClick={startTrading}
                    >
                      🚀 Start Trading
                    </button>
                  ) : (
                    <button 
                      className="stop-trading-btn"
                      onClick={stopTrading}
                    >
                      ⏹️ Stop Trading
                    </button>
                  )}
                  <button 
                    className="restart-session-btn"
                    onClick={restartTradingSession}
                  >
                    🔄 Restart Session
                  </button>
                  {tradingStatus && (
                    <div className="trading-status">
                      {tradingStatus}
                    </div>
                  )}
                </div>
              </div>

                                      <div className="config-section">
                          <h3>Pine Script Strategies</h3>
                          {strategyStatus && (
                            <div className="strategy-status">
                              {strategyStatus}
                            </div>
                          )}
                          
                          <div className="strategy-editors">
                            <div className="strategy-editor">
                              <h4>BTC Strategy</h4>
                              <textarea
                                value={btcStrategy}
                                onChange={(e) => setBtcStrategy(e.target.value)}
                                placeholder="// Pine Script for BTC
// Example: Moving Average Crossover
fastMA = sma(close, 10)
slowMA = sma(close, 20)

buySignal = fastMA > slowMA and fastMA[1] <= slowMA[1]
sellSignal = fastMA < slowMA and fastMA[1] >= slowMA[1]

if buySignal
    strategy.entry('Long', strategy.long)
if sellSignal
    strategy.close('Long')"
                                className="pine-script-editor"
                              />
                              <button 
                                className="update-strategy-btn"
                                onClick={() => updateStrategy('BTC', btcStrategy)}
                              >
                                Update BTC Strategy
                              </button>
                            </div>
                            
                            <div className="strategy-editor">
                              <h4>ETH Strategy</h4>
                              <textarea
                                value={ethStrategy}
                                onChange={(e) => setEthStrategy(e.target.value)}
                                placeholder="// Pine Script for ETH
// Example: RSI Strategy
rsi = rsi(close, 14)

buySignal = rsi < 30
sellSignal = rsi > 70

if buySignal
    strategy.entry('Long', strategy.long)
if sellSignal
    strategy.close('Long')"
                                className="pine-script-editor"
                              />
                              <button 
                                className="update-strategy-btn"
                                onClick={() => updateStrategy('ETH', ethStrategy)}
                              >
                                Update ETH Strategy
                              </button>
                            </div>
                          </div>
                        </div>

                        <div className="config-section">
                          <h3>Trade History</h3>
                          <div className="trades-container">
                            {tradesHistory.length > 0 ? (
                              tradesHistory.map((trade, index) => (
                                <div key={index} className="trade-entry">
                                  <div className="trade-header">
                                    <span className="trade-time">{formatTradeTimestamp(trade.timestamp)}</span>
                                    <span className={`trade-action ${trade.action.toLowerCase()}`}>
                                      {trade.action}
                                    </span>
                                    <span className="trade-symbol">{trade.symbol}</span>
                                  </div>
                                  <div className="trade-details">
                                    <span className="trade-quantity">Qty: {trade.quantity}</span>
                                    <span className="trade-price">Price: {formatCurrency(trade.price)}</span>
                                    <span className="trade-total">Total: {formatTradeAmount(trade.quantity, trade.price)}</span>
                                    {trade.pnl !== null && trade.pnl !== undefined && trade.pnl !== 0 && (
                                      <span className={`trade-pnl ${trade.pnl >= 0 ? 'positive' : 'negative'}`}>
                                        P&L: {formatCurrency(trade.pnl)}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="no-trades">No trades available</p>
                            )}
                          </div>
                        </div>

                        <div className="config-section">
                          <h3>Trading Logs</h3>
                          <div className="logs-container">
                            {tradingLogs.length > 0 ? (
                              tradingLogs.map((log, index) => (
                                <div key={index} className="log-entry">
                                  <span className="log-time">{formatLogTimestamp(log.timestamp)}</span>
                                  <span className={`log-level ${log.level}`}>{log.level.toUpperCase()}</span>
                                  <span className="log-message">{log.message}</span>
                                </div>
                              ))
                            ) : (
                              <p className="no-logs">No trading logs available</p>
                            )}
                          </div>
                        </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
