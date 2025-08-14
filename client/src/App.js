import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';
import TradingViewWidget from './components/TradingViewWidget';
import AdvancedPineScriptEditor from './components/AdvancedPineScriptEditor';
import ErrorBoundary from './components/ErrorBoundary';

// Notification component
const Notification = ({ type, title, message, onClose }) => {
  const getIcon = () => {
    switch (type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📢';
    }
  };

  return (
    <div className={`notification ${type}`}>
      <div className="notification-icon">{getIcon()}</div>
      <div className="notification-content">
        <div className="notification-title">{title}</div>
        <div className="notification-message">{message}</div>
      </div>
      <button className="notification-close" onClick={onClose}>×</button>
    </div>
  );
};

function App() {
  // Temporarily disable error suppression to debug white screen
  useEffect(() => {
    console.log('App component mounted - checking for errors...');
    
    // Keep basic error handling but allow errors to show
    const originalError = console.error;
    const originalWarn = console.warn;
    
    console.error = function(...args) {
      const message = args.join(' ');
      console.log('ERROR CAUGHT:', message);
      originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
      const message = args.join(' ');
      console.log('WARNING CAUGHT:', message);
      originalWarn.apply(console, args);
    };

    // Allow window errors to show
    const originalErrorHandler = window.onerror;
    window.onerror = function(msg, url, line, col, error) {
      console.log('WINDOW ERROR:', msg, url, line, col);
      if (originalErrorHandler) {
        return originalErrorHandler(msg, url, line, col, error);
      }
      return false;
    };

    // Allow unhandled promise rejections to show
    const originalUnhandledRejection = window.onunhandledrejection;
    window.onunhandledrejection = function(event) {
      console.log('UNHANDLED REJECTION:', event.reason);
      if (originalUnhandledRejection) {
        originalUnhandledRejection(event);
      }
    };

    return () => {
      console.error = originalError;
      console.warn = originalWarn;
      window.onerror = originalErrorHandler;
      window.onunhandledrejection = originalUnhandledRejection;
    };
  }, []);

  const [backendStatus, setBackendStatus] = useState('Checking...');
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
  const [tradesHistory, setTradesHistory] = useState([]);
  const [showConfig, setShowConfig] = useState(false);
  const [tradingMode, setTradingMode] = useState('paper');
  const [isTradingActive, setIsTradingActive] = useState(false);
  const [btcStrategy, setBtcStrategy] = useState('');
  const [ethStrategy, setEthStrategy] = useState('');
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
  const [notifications, setNotifications] = useState([]);

  const timestampRef = useRef();

  // Notification functions
  const addNotification = useCallback((type, title, message) => {
    const id = Date.now();
    const newNotification = { id, type, title, message };
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(id);
    }, 5000);
  }, []);

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  // Fetch functions - moved outside useEffect for global access
  const updateTimestamp = useCallback(() => {
    if (timestampRef.current) {
      timestampRef.current.textContent = new Date().toLocaleString();
    }
  }, []);

  const fetchSystemStatus = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/status');
      if (response.ok) {
        await response.json();
        setBackendStatus('Online');
      } else {
        setBackendStatus('Offline');
      }
    } catch (error) {
      setBackendStatus('Offline');
      addNotification('error', 'Connection Error', 'Failed to connect to backend server');
    }
  }, [addNotification]);

  const fetchPortfolioData = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/data/portfolio-metrics');
      if (response.ok) {
        const data = await response.json();
        setPortfolioData(data.data);
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      addNotification('error', 'Data Error', 'Failed to fetch portfolio metrics');
    }
  }, [addNotification]);

  const fetchTotalAssets = useCallback(async () => {
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
          
          // Add notification for successful API retrieval
          addNotification('info', 'Market Data Updated', `BTC: $${btcPrice.toFixed(2)} | ETH: $${ethPrice.toFixed(2)}`);
        }
      }
    } catch (error) {
      console.error('Error fetching total assets:', error);
      addNotification('error', 'Market Data Error', 'Failed to fetch latest prices from Coinbase');
    }
  }, [addNotification]);

  const fetchTradingLogs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/trading-logs');
      if (response.ok) {
        const data = await response.json();
        setTradingLogs(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching trading logs:', error);
    }
  }, []);

  const fetchTradingStatus = useCallback(async () => {
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
  }, []);

  const fetchTradesHistory = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/trading/history?limit=50');
      if (response.ok) {
        const result = await response.json();
        setTradesHistory(result.data || []);
      }
    } catch (error) {
      console.error('Error fetching trades history:', error);
    }
  }, []);

  const fetchAdvancedMetrics = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/data/advanced-metrics');
      if (response.ok) {
        const data = await response.json();
        setAdvancedMetrics(data.data || {});
      }
    } catch (error) {
      console.error('Error fetching advanced metrics:', error);
    }
  }, []);

  const fetchStrategies = useCallback(async () => {
    try {
      const [btcResponse, ethResponse] = await Promise.all([
        fetch('http://localhost:5000/api/strategies/BTC'),
        fetch('http://localhost:5000/api/strategies/ETH')
      ]);
      
      if (btcResponse.ok) {
        const btcData = await btcResponse.json();
        if (btcData.success && btcData.data) {
          setBtcStrategy(btcData.data.code || '');
        }
      }
      
      if (ethResponse.ok) {
        const ethData = await ethResponse.json();
        if (ethData.success && ethData.data) {
          setEthStrategy(ethData.data.code || '');
        }
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchSystemStatus();
    fetchPortfolioData();
    fetchTotalAssets();
    fetchTradingLogs();
    fetchTradingStatus();
    fetchTradesHistory();
    fetchAdvancedMetrics();
    fetchStrategies();
    
    // Welcome notification
    addNotification('info', 'TradeX Dashboard', 'Welcome! Dashboard is now active and monitoring your trading system.');

    // Set up intervals for real-time updates (5 seconds for all data)
    const timestampInterval = setInterval(updateTimestamp, 1000);
    const statusInterval = setInterval(fetchSystemStatus, 10000);
    const dataInterval = setInterval(fetchPortfolioData, 5000); // 5 seconds
    const assetsInterval = setInterval(fetchTotalAssets, 5000); // 5 seconds
    const logsInterval = setInterval(fetchTradingLogs, 5000); // 5 seconds
    const tradingStatusInterval = setInterval(fetchTradingStatus, 10000); // 10 seconds
    const tradesInterval = setInterval(fetchTradesHistory, 5000); // 5 seconds
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
  }, [fetchSystemStatus, fetchPortfolioData, fetchTotalAssets, fetchTradingLogs, fetchTradingStatus, fetchTradesHistory, fetchAdvancedMetrics, fetchStrategies, updateTimestamp, addNotification]);

  const startTrading = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/start-trading', {
        method: 'POST'
      });
      
      if (response.ok) {
        setIsTradingActive(true);
        addNotification('success', 'Trading Started', 'Trading system is now active and making decisions!');
        
        // Immediately refresh data after starting
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
        
        // Verify the status after a short delay
        setTimeout(() => {
          fetchTradingStatus();
        }, 1000);
      } else {
        addNotification('error', 'Failed to Start Trading', 'Could not start trading system');
      }
    } catch (error) {
      addNotification('error', 'Failed to Start Trading', 'Error connecting to server');
    }
  };

  const stopTrading = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/stop-trading', {
        method: 'POST'
      });
      
      if (response.ok) {
        setIsTradingActive(false);
        addNotification('info', 'Trading Stopped', 'Trading system has been stopped');
        
        // Immediately refresh data after stopping
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
        
        // Verify the status after a short delay
        setTimeout(() => {
          fetchTradingStatus();
        }, 1000);
      } else {
        addNotification('error', 'Failed to Stop Trading', 'Could not stop trading system');
      }
    } catch (error) {
      addNotification('error', 'Failed to Stop Trading', 'Error connecting to server');
    }
  };

  const restartTradingSession = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/system/restart-session', {
        method: 'POST'
      });
      
      if (response.ok) {
        addNotification('success', 'Session Restarted', 'Trading session restarted - all data cleared');
        
        // Immediately refresh data after restart
        fetchPortfolioData();
        fetchTotalAssets();
        fetchTradesHistory();
        fetchTradingLogs();
      } else {
        addNotification('error', 'Failed to Restart Session', 'Could not restart trading session');
      }
    } catch (error) {
      addNotification('error', 'Failed to Restart Session', 'Error connecting to server');
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
        addNotification('info', 'Trading Mode Changed', `Switched to ${newMode.toUpperCase()} trading mode`);
        
        if (newMode === 'real') {
          addNotification('warning', 'Real Trading Mode', 'Some metrics may show "API Error" as they require Coinbase API credentials');
        }
      } else {
        addNotification('error', 'Mode Switch Failed', 'Failed to switch trading mode');
      }
    } catch (error) {
      addNotification('error', 'Mode Switch Error', 'Error connecting to server');
    }
  };

  const validatePineScript = async (code) => {
    // Basic Pine Script validation
    if (!code.trim()) {
      return { valid: true, error: null };
    }

    const errors = [];
    
    // Check for basic syntax
    if (!code.includes('return')) {
      errors.push('Missing return statement');
    }
    
    if (!code.includes('action')) {
      errors.push('Missing action field in return object');
    }
    
    if (!code.includes('confidence')) {
      errors.push('Missing confidence field in return object');
    }
    
    // Check for common Pine Script patterns
    const requiredPatterns = [
      /ta\./,
      /close/,
      /high/,
      /low/
    ];
    
    const hasRequiredPatterns = requiredPatterns.some(pattern => pattern.test(code));
    if (!hasRequiredPatterns) {
      errors.push('Missing common Pine Script indicators or price data');
    }

    return {
      valid: errors.length === 0,
      error: errors.length > 0 ? errors.join(', ') : null
    };
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
        addNotification('success', 'Strategy Updated', `${symbol} strategy updated successfully`);
      } else {
        addNotification('error', 'Strategy Update Failed', `Failed to update ${symbol} strategy`);
      }
    } catch (error) {
      addNotification('error', 'Strategy Update Error', `Error updating ${symbol} strategy`);
    }
  };

  const formatCurrency = (value) => {
    if (value === 'API Error' || value === null || value === undefined) {
      return 'API Error';
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (value === 'API Error' || value === null || value === undefined) {
      return 'API Error';
    }
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
            <span className={`status-value ${backendStatus.includes('Online') ? 'online' : 'offline'}`}>
              {backendStatus.includes('Online') ? 'Online' : 'Offline'}
            </span>
          </div>
          <div className="status-item">
            <span>Frontend:</span>
            <span className="status-value online">Online</span>
          </div>
          <div className="status-item">
            <span>Database:</span>
            <span className="status-value online">Online</span>
          </div>
          <div className="status-item">
            <span>API:</span>
            <span className="status-value online">Online</span>
          </div>
        </div>

        <div className="nav-section">
          <h3>Market Data</h3>
          <div className="market-item">
            <span>BTC:</span>
            <span className="price">${(marketData.BTC?.price || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
          <div className="market-item">
            <span>ETH:</span>
            <span className="price">${(marketData.ETH?.price || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
        </div>

        <div className="nav-section">
          <h3>Advanced Metrics</h3>
          <div className="metric-item">
            <span>Volatility:</span>
            <span>{formatPercentage(advancedMetrics?.volatility || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Correlation:</span>
            <span>{formatPercentage(advancedMetrics?.correlation || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Market Regime:</span>
            <span className={`regime ${advancedMetrics?.marketRegime || 'sideways'}`}>
              {advancedMetrics?.marketRegime || 'sideways'}
            </span>
          </div>
          <div className="metric-item">
            <span>Signal Strength:</span>
            <span>{formatPercentage(advancedMetrics?.signalStrength || 0)}</span>
          </div>
          <div className="metric-item">
            <span>Risk Score:</span>
            <span className={`risk ${(advancedMetrics?.riskScore || 0) > 70 ? 'high' : (advancedMetrics?.riskScore || 0) > 40 ? 'medium' : 'low'}`}>
              {formatPercentage(advancedMetrics?.riskScore || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <div className="header">
          <div className="header-left">
            {/* Program Updates Panel */}
            <div className="notifications-panel">
              <h3>Program Updates</h3>
              <div className="notifications">
                {notifications.length > 0 ? (
                  notifications.map(notification => (
                    <Notification
                      key={notification.id}
                      type={notification.type}
                      title={notification.title}
                      message={notification.message}
                      onClose={() => removeNotification(notification.id)}
                    />
                  ))
                ) : (
                  <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px', textAlign: 'center', padding: '10px' }}>
                    No recent updates
                  </div>
                )}
              </div>
            </div>
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



        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="card">
            <div className="card-header">Total P&L</div>
            <div className={`card-value ${portfolioData.totalPL === 'API Error' ? 'negative' : portfolioData.totalPL > 0 ? 'positive' : portfolioData.totalPL < 0 ? 'negative' : 'neutral'}`}>
              {formatCurrency(portfolioData.totalPL)}
            </div>
            <div className="card-subtitle">Realized + Unrealized</div>
          </div>
          
          <div className="card">
            <div className="card-header">Total Trades</div>
            <div className={`card-value ${portfolioData.totalTrades === 'API Error' ? 'negative' : portfolioData.totalTrades > 0 ? 'positive' : 'neutral'}`}>
              {portfolioData.totalTrades === 'API Error' ? 'API Error' : portfolioData.totalTrades}
            </div>
            <div className="card-subtitle">Win Rate: {formatPercentage(portfolioData.winRate)}</div>
          </div>
          
          <div className="card">
            <div className="card-header">Portfolio Value</div>
            <div className={`card-value ${portfolioData.portfolioValue === 'API Error' ? 'negative' : portfolioData.portfolioValue > 1000 ? 'positive' : portfolioData.portfolioValue < 1000 ? 'negative' : 'neutral'}`}>
              {formatCurrency(portfolioData.portfolioValue)}
            </div>
            <div className="card-subtitle">Starting: $1,000.00</div>
          </div>
          
          <div className="card">
            <div className="card-header">Total Assets</div>
            <div className={`card-value ${totalAssets.totalValue === 'API Error' ? 'negative' : totalAssets.totalValue > 0 ? 'positive' : 'neutral'}`}>
              {formatCurrency(totalAssets.totalValue)}
            </div>
            <div className="card-subtitle">BTC: {formatCurrency(totalAssets.btcValue)} | ETH: {formatCurrency(totalAssets.ethValue)}</div>
          </div>
        </div>

        {/* Advanced Performance Metrics */}
        <div className="advanced-metrics">
          <h3>Advanced Performance Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Average Win</div>
              <div className={`metric-value ${portfolioData.avgWin === 'API Error' ? 'negative' : portfolioData.avgWin > 0 ? 'positive' : 'neutral'}`}>
                {formatCurrency(portfolioData.avgWin)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Average Loss</div>
              <div className={`metric-value ${portfolioData.avgLoss === 'API Error' ? 'negative' : portfolioData.avgLoss > 0 ? 'negative' : 'neutral'}`}>
                {formatCurrency(portfolioData.avgLoss)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Profit Factor</div>
              <div className={`metric-value ${portfolioData.profitFactor === 'API Error' ? 'negative' : (portfolioData.profitFactor || 0) > 1.5 ? 'positive' : (portfolioData.profitFactor || 0) < 1.0 ? 'negative' : 'neutral'}`}>
                {portfolioData.profitFactor === 'API Error' ? 'API Error' : (portfolioData.profitFactor || 0).toFixed(2)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Max Drawdown</div>
              <div className={`metric-value ${portfolioData.maxDrawdown === 'API Error' ? 'negative' : (portfolioData.maxDrawdown || 0) < 10 ? 'positive' : (portfolioData.maxDrawdown || 0) > 20 ? 'negative' : 'neutral'}`}>
                {portfolioData.maxDrawdown === 'API Error' ? 'API Error' : formatPercentage(portfolioData.maxDrawdown || 0)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Sharpe Ratio</div>
              <div className={`metric-value ${portfolioData.sharpeRatio === 'API Error' ? 'negative' : (portfolioData.sharpeRatio || 0) > 1.0 ? 'positive' : (portfolioData.sharpeRatio || 0) < 0.5 ? 'negative' : 'neutral'}`}>
                {portfolioData.sharpeRatio === 'API Error' ? 'API Error' : (portfolioData.sharpeRatio || 0).toFixed(2)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Winning Trades</div>
              <div className={`metric-value ${portfolioData.winningTrades === 'API Error' ? 'negative' : portfolioData.winningTrades > 0 ? 'positive' : 'neutral'}`}>
                {portfolioData.winningTrades === 'API Error' ? 'API Error' : (portfolioData.winningTrades || 0)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Losing Trades</div>
              <div className={`metric-value ${portfolioData.losingTrades === 'API Error' ? 'negative' : portfolioData.losingTrades > 0 ? 'negative' : 'neutral'}`}>
                {portfolioData.losingTrades === 'API Error' ? 'API Error' : (portfolioData.losingTrades || 0)}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Risk/Reward</div>
              <div className={`metric-value ${portfolioData.avgLoss === 'API Error' || portfolioData.avgWin === 'API Error' ? 'negative' : (portfolioData.avgLoss || 0) > 0 ? ((portfolioData.avgWin || 0) / (portfolioData.avgLoss || 1)) > 2.0 ? 'positive' : ((portfolioData.avgWin || 0) / (portfolioData.avgLoss || 1)) < 1.5 ? 'negative' : 'neutral' : 'neutral'}`}>
                {portfolioData.avgLoss === 'API Error' || portfolioData.avgWin === 'API Error' ? 'API Error' : ((portfolioData.avgLoss || 0) > 0 ? ((portfolioData.avgWin || 0) / (portfolioData.avgLoss || 1)).toFixed(2) : 'N/A')}
              </div>
            </div>
          </div>
        </div>

        {/* TradingView Charts */}
        <div className="charts-section">
          <div className="charts-grid">
            <div className="chart-panel">
              <h4>BTC/USD Chart</h4>
              <ErrorBoundary>
                <TradingViewWidget symbol="BTC" />
              </ErrorBoundary>
            </div>
            <div className="chart-panel">
              <h4>ETH/USD Chart</h4>
              <ErrorBoundary>
                <TradingViewWidget symbol="ETH" />
              </ErrorBoundary>
            </div>
          </div>
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
                <h3>Advanced Pine Script Strategies</h3>
                <div className="strategy-editors">
                  <div className="strategy-editor">
                    <h4>BTC Strategy</h4>
                    <AdvancedPineScriptEditor
                      value={btcStrategy}
                      onChange={setBtcStrategy}
                      placeholder="Enter Pine Script strategy for BTC..."
                      onSave={() => updateStrategy('BTC', btcStrategy)}
                      onValidate={validatePineScript}
                      symbol="BTC"
                    />
                    <button onClick={() => updateStrategy('BTC', btcStrategy)}>
                      Update BTC Strategy
                    </button>
                  </div>
                  <div className="strategy-editor">
                    <h4>ETH Strategy</h4>
                    <AdvancedPineScriptEditor
                      value={ethStrategy}
                      onChange={setEthStrategy}
                      placeholder="Enter Pine Script strategy for ETH..."
                      onSave={() => updateStrategy('ETH', ethStrategy)}
                      onValidate={validatePineScript}
                      symbol="ETH"
                    />
                    <button onClick={() => updateStrategy('ETH', ethStrategy)}>
                      Update ETH Strategy
                    </button>
                  </div>
                </div>
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
