import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import TradingViewWidget from './components/TradingViewWidget';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [systemStatus, setSystemStatus] = useState({});
  const [portfolioData, setPortfolioData] = useState({
    totalPL: 0,
    totalTrades: 0,
    portfolioValue: 0,
    winRate: 0,
    avgWin: 0,
    avgLoss: 0,
    profitFactor: 0,
    maxDrawdown: 0,
    sharpeRatio: 0,
    totalAssets: 0
  });
  const [totalAssets, setTotalAssets] = useState({
    btcValue: 0,
    ethValue: 0,
    totalValue: 0
  });
  const [tradingLogs, setTradingLogs] = useState([]);
  const [tradingStatus, setTradingStatus] = useState('');
  const [tradesHistory, setTradesHistory] = useState([]);
  const [showConfig, setShowConfig] = useState(false);
  const [tradingMode, setTradingMode] = useState('paper');
  const [isTradingActive, setIsTradingActive] = useState(false);
  const [btcStrategy, setBtcStrategy] = useState('');
  const [ethStrategy, setEthStrategy] = useState('');
  const [strategyStatus, setStrategyStatus] = useState('');
  const [marketData, setMarketData] = useState({
    BTC: { price: 0, change24h: 0 },
    ETH: { price: 0, change24h: 0 }
  });
  const [advancedMetrics, setAdvancedMetrics] = useState({
    volatility: 0,
    correlation: 0,
    marketRegime: 'sideways',
    signalStrength: 0,
    riskScore: 0
  });

  const timestampRef = useRef();

  useEffect(() => {
    const updateTimestamp = () => {
      if (timestampRef.current) {
        timestampRef.current.textContent = new Date().toLocaleString();
      }
    };

    const fetchSystemStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/system/status');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data.data);
          setBackendStatus('🟢 Online');
        } else {
          setBackendStatus('🔴 Offline');
        }
      } catch (error) {
        setBackendStatus('🔴 Offline');
      }
    };

    const fetchPortfolioData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data/portfolio-metrics');
        if (response.ok) {
          const data = await response.json();
          setPortfolioData(data.data);
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
            
            setTotalAssets({
              btcValue: btcValue,
              ethValue: ethValue,
              totalValue: totalValue
            });

            // Update market data
            setMarketData({
              BTC: { price: btcPrice, change24h: 0 },
              ETH: { price: ethPrice, change24h: 0 }
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
          setTradingLogs(data.data || []);
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
          setTradingMode(data.tradingMode || 'paper');
          setIsTradingActive(data.isActive || false);
        }
      } catch (error) {
        console.error('Error fetching trading status:', error);
      }
    };

    const fetchTradesHistory = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/trading/history?limit=50');
        if (response.ok) {
          const result = await response.json();
          setTradesHistory(result.data || []);
        }
      } catch (error) {
        console.error('Error fetching trades history:', error);
      }
    };

    const fetchAdvancedMetrics = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data/advanced-metrics');
        if (response.ok) {
          const data = await response.json();
          setAdvancedMetrics(data.data || {});
        }
      } catch (error) {
        console.error('Error fetching advanced metrics:', error);
      }
    };

    // Initial fetch
    fetchSystemStatus();
    fetchPortfolioData();
    fetchTotalAssets();
    fetchTradingLogs();
    fetchTradingStatus();
    fetchTradesHistory();
    fetchAdvancedMetrics();

    // Set up intervals for real-time updates (1 second for critical data)
    const timestampInterval = setInterval(updateTimestamp, 1000);
    const statusInterval = setInterval(fetchSystemStatus, 10000);
    const dataInterval = setInterval(fetchPortfolioData, 1000); // 1 second
    const assetsInterval = setInterval(fetchTotalAssets, 1000); // 1 second
    const logsInterval = setInterval(fetchTradingLogs, 1000); // 1 second
    const tradingStatusInterval = setInterval(fetchTradingStatus, 1000); // 1 second
    const tradesInterval = setInterval(fetchTradesHistory, 1000); // 1 second
    const advancedMetricsInterval = setInterval(fetchAdvancedMetrics, 5000); // 5 seconds

    return () => {
      clearInterval(timestampInterval);
      clearInterval(statusInterval);
      clearInterval(dataInterval);
      clearInterval(assetsInterval);
      clearInterval(logsInterval);
      clearInterval(tradingStatusInterval);
      clearInterval(tradesInterval);
      clearInterval(advancedMetricsInterval);
    };
  }, []);

  const startTrading = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/start-trading', {
        method: 'POST'
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
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      }
    } catch (error) {
      setTradingStatus('❌ Error starting trading system');
      setTimeout(() => {
        setTradingStatus('');
      }, 5000);
    }
  };

  const stopTrading = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/stop-trading', {
        method: 'POST'
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
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      }
    } catch (error) {
      setTradingStatus('❌ Error stopping trading system');
      setTimeout(() => {
        setTradingStatus('');
      }, 5000);
    }
  };

  const restartTradingSession = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/restart-session', {
        method: 'POST'
      });
      
      if (response.ok) {
        setTradingStatus('🔄 Trading session restarted - all data cleared');
        
        // Immediately refresh data after restart
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
        
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      } else {
        setTradingStatus('❌ Failed to restart trading session');
        setTimeout(() => {
          setTradingStatus('');
        }, 5000);
      }
    } catch (error) {
      setTradingStatus('❌ Error restarting trading session');
      setTimeout(() => {
        setTradingStatus('');
      }, 5000);
    }
  };

  const toggleTradingMode = async () => {
    try {
      const newMode = tradingMode === 'paper' ? 'real' : 'paper';
      const response = await fetch('http://localhost:5000/api/system/trading-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: newMode })
      });
      
      if (response.ok) {
        setTradingMode(newMode);
        setTradingStatus(`🔄 Trading mode switched to ${newMode.toUpperCase()} trading`);
        setTimeout(() => {
          setTradingStatus('');
        }, 3000);
      }
    } catch (error) {
      setTradingStatus('❌ Error switching trading mode');
      setTimeout(() => {
        setTradingStatus('');
      }, 3000);
    }
  };

  const updateStrategy = async (symbol, code) => {
    try {
      const response = await fetch(`http://localhost:5000/api/system/update-strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol, code })
      });
      
      if (response.ok) {
        setStrategyStatus(`✅ ${symbol} strategy updated successfully`);
        setTimeout(() => {
          setStrategyStatus('');
        }, 3000);
      } else {
        setStrategyStatus(`❌ Failed to update ${symbol} strategy`);
        setTimeout(() => {
          setStrategyStatus('');
        }, 3000);
      }
    } catch (error) {
      setStrategyStatus(`❌ Error updating ${symbol} strategy`);
      setTimeout(() => {
        setStrategyStatus('');
      }, 3000);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  const formatTradeTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (error) {
      return timestamp;
    }
  };

  return (
    <div className="App">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo">
          <img src="/TradeX-Logo.png" alt="TradeX Logo" />
        </div>
        
        <div className="nav-section">
          <h3>System Status</h3>
          <div className="status-item">
            <span>Backend:</span>
            <span className="status-value">{backendStatus}</span>
          </div>
          <div className="status-item">
            <span>Frontend:</span>
            <span className="status-value">🟢 Online</span>
          </div>
          <div className="status-item">
            <span>Database:</span>
            <span className="status-value">🟢 Online</span>
          </div>
          <div className="status-item">
            <span>API:</span>
            <span className="status-value">🟢 Online</span>
          </div>
        </div>

        <div className="nav-section">
          <h3>Market Data</h3>
          <div className="market-item">
            <span>BTC:</span>
            <span className="price">${marketData.BTC.price.toFixed(2)}</span>
          </div>
          <div className="market-item">
            <span>ETH:</span>
            <span className="price">${marketData.ETH.price.toFixed(2)}</span>
          </div>
        </div>

        <div className="nav-section">
          <h3>Advanced Metrics</h3>
          <div className="metric-item">
            <span>Volatility:</span>
            <span>{formatPercentage(advancedMetrics.volatility || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Correlation:</span>
            <span>{formatPercentage(advancedMetrics.correlation || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Market Regime:</span>
            <span className={`regime ${advancedMetrics.marketRegime || 'sideways'}`}>
              {advancedMetrics.marketRegime || 'sideways'}
            </span>
          </div>
          <div className="metric-item">
            <span>Signal Strength:</span>
            <span>{formatPercentage(advancedMetrics.signalStrength || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Risk Score:</span>
            <span className={`risk ${advancedMetrics.riskScore > 70 ? 'high' : advancedMetrics.riskScore > 40 ? 'medium' : 'low'}`}>
              {formatPercentage(advancedMetrics.riskScore || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <div className="header">
          <div className="header-left">
            <h1>TradeX Dashboard</h1>
            <p>Advanced Cryptocurrency Trading Bot</p>
          </div>
          <div className="header-right">
            <div className="timestamp">
              Last Updated: <span ref={timestampRef}>{new Date().toLocaleString()}</span>
            </div>
            <button className="config-btn" onClick={() => setShowConfig(true)}>
              Trading Configuration
            </button>
          </div>
        </div>

        {/* Trading Status */}
        {tradingStatus && (
          <div className="trading-status">
            {tradingStatus}
          </div>
        )}

        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="card">
            <div className="card-header">Total P&L</div>
            <div className={`card-value ${portfolioData.totalPL >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(portfolioData.totalPL)}
            </div>
            <div className="card-subtitle">Realized + Unrealized</div>
          </div>
          
          <div className="card">
            <div className="card-header">Total Trades</div>
            <div className="card-value">{portfolioData.totalTrades}</div>
            <div className="card-subtitle">Win Rate: {formatPercentage(portfolioData.winRate)}</div>
          </div>
          
          <div className="card">
            <div className="card-header">Portfolio Value</div>
            <div className="card-value">{formatCurrency(portfolioData.portfolioValue)}</div>
            <div className="card-subtitle">Starting: $1,000.00</div>
          </div>
          
          <div className="card">
            <div className="card-header">Total Assets</div>
            <div className="card-value">{formatCurrency(totalAssets.totalValue)}</div>
            <div className="card-subtitle">BTC: {formatCurrency(totalAssets.btcValue)} | ETH: {formatCurrency(totalAssets.ethValue)}</div>
          </div>
        </div>

        {/* Advanced Performance Metrics */}
        <div className="advanced-metrics">
          <h3>Advanced Performance Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Average Win</div>
              <div className="metric-value positive">{formatCurrency(portfolioData.avgWin)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Average Loss</div>
              <div className="metric-value negative">{formatCurrency(portfolioData.avgLoss)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Profit Factor</div>
              <div className="metric-value">{portfolioData.profitFactor.toFixed(2)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Max Drawdown</div>
              <div className="metric-value negative">{formatPercentage(portfolioData.maxDrawdown)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Sharpe Ratio</div>
              <div className="metric-value">{portfolioData.sharpeRatio.toFixed(2)}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Winning Trades</div>
              <div className="metric-value">{portfolioData.winningTrades || 0}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Losing Trades</div>
              <div className="metric-value">{portfolioData.losingTrades || 0}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Risk/Reward</div>
              <div className="metric-value">
                {portfolioData.avgLoss > 0 ? (portfolioData.avgWin / portfolioData.avgLoss).toFixed(2) : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* TradingView Charts */}
        <div className="charts-section">
          <h3>Live Market Charts</h3>
          <TradingViewWidget />
        </div>
      </div>

      {/* Configuration Panel */}
      {showConfig && (
        <div className="config-overlay">
          <div className="config-panel">
            <div className="config-header">
              <h2>Trading Configuration</h2>
              <button className="close-btn" onClick={() => setShowConfig(false)}>×</button>
            </div>

            <div className="config-content">
              {/* Trading Mode Section */}
              <div className="config-section">
                <h3>Trading Mode</h3>
                <div className="trading-mode-controls">
                  <div className="mode-toggle">
                    <span>Paper Trading</span>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={tradingMode === 'real'}
                        onChange={toggleTradingMode}
                      />
                      <span className="slider"></span>
                    </label>
                    <span>Real Trading</span>
                  </div>
                  <div className="mode-status">
                    Current Mode: <strong>{tradingMode.toUpperCase()}</strong>
                  </div>
                </div>
              </div>

              {/* Trading Control Section */}
              <div className="config-section">
                <h3>Trading Control</h3>
                <div className="trading-controls">
                  <button
                    className={`control-btn ${isTradingActive ? 'stop' : 'start'}`}
                    onClick={isTradingActive ? stopTrading : startTrading}
                  >
                    {isTradingActive ? 'Stop Trading' : 'Start Trading'}
                  </button>
                  <button className="control-btn restart" onClick={restartTradingSession}>
                    Restart Trading Session
                  </button>
                </div>
                <div className="trading-status-display">
                  Status: <strong>{isTradingActive ? 'ACTIVE' : 'STOPPED'}</strong>
                </div>
              </div>

              {/* Pine Script Strategies Section */}
              <div className="config-section">
                <h3>Pine Script Strategies</h3>
                <div className="strategy-editors">
                  <div className="strategy-editor">
                    <h4>BTC Strategy</h4>
                    <textarea
                      value={btcStrategy}
                      onChange={(e) => setBtcStrategy(e.target.value)}
                      placeholder="Enter Pine Script strategy for BTC..."
                    />
                    <button onClick={() => updateStrategy('BTC', btcStrategy)}>
                      Update BTC Strategy
                    </button>
                  </div>
                  <div className="strategy-editor">
                    <h4>ETH Strategy</h4>
                    <textarea
                      value={ethStrategy}
                      onChange={(e) => setEthStrategy(e.target.value)}
                      placeholder="Enter Pine Script strategy for ETH..."
                    />
                    <button onClick={() => updateStrategy('ETH', ethStrategy)}>
                      Update ETH Strategy
                    </button>
                  </div>
                </div>
                {strategyStatus && (
                  <div className="strategy-status">{strategyStatus}</div>
                )}
              </div>

              {/* Trade History Section */}
              <div className="config-section">
                <h3>Trade History</h3>
                <div className="trades-container">
                  {tradesHistory.length > 0 ? (
                    tradesHistory.map((trade, index) => (
                      <div key={index} className="trade-entry">
                        <div className="trade-time">{formatTradeTimestamp(trade.timestamp)}</div>
                        <div className={`trade-action ${trade.action.toLowerCase()}`}>
                          {trade.action}
                        </div>
                        <div className="trade-symbol">{trade.symbol}</div>
                        <div className="trade-quantity">{trade.quantity}</div>
                        <div className="trade-price">${trade.price}</div>
                        <div className="trade-status">{trade.status}</div>
                      </div>
                    ))
                  ) : (
                    <div className="no-trades">No trades available</div>
                  )}
                </div>
              </div>

              {/* Trading Logs Section */}
              <div className="config-section">
                <h3>Trading Logs</h3>
                <div className="logs-container">
                  {tradingLogs.length > 0 ? (
                    tradingLogs.map((log, index) => (
                      <div key={index} className="log-entry">
                        <div className="log-time">{formatTradeTimestamp(log.timestamp)}</div>
                        <div className={`log-level ${log.level.toLowerCase()}`}>
                          {log.level}
                        </div>
                        <div className="log-message">{log.message}</div>
                      </div>
                    ))
                  ) : (
                    <div className="no-logs">No trading logs available</div>
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
