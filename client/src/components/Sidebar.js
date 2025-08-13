import React, { useState, useEffect } from 'react';

const Sidebar = () => {
  const [systemStatus, setSystemStatus] = useState({
    dataRetriever: 'online',
    logicEngine: 'online',
    executor: 'online'
  });

  const [systemMetrics, setSystemMetrics] = useState({
    uptime: '0h 0m',
    memory: '0%',
    cpu: '0%',
    trades: 0
  });

  useEffect(() => {
    // Fetch system status from backend
    const fetchSystemStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/system/status');
        const data = await response.json();
        
        // Update system metrics
        const uptimeHours = Math.floor(data.uptime / 3600);
        const uptimeMinutes = Math.floor((data.uptime % 3600) / 60);
        const memoryUsage = Math.round((data.memory.heapUsed / data.memory.heapTotal) * 100);
        
        setSystemMetrics({
          uptime: `${uptimeHours}h ${uptimeMinutes}m`,
          memory: `${memoryUsage}%`,
          cpu: '0%', // CPU usage not available in current API
          trades: 0 // Will be updated from performance API
        });
      } catch (error) {
        console.error('Error fetching system status:', error);
      }
    };

    // Fetch performance data
    const fetchPerformance = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/performance/metrics');
        const data = await response.json();
        setSystemMetrics(prev => ({
          ...prev,
          trades: data.totalTrades || 0
        }));
      } catch (error) {
        console.error('Error fetching performance data:', error);
      }
    };

    // Initial fetch
    fetchSystemStatus();
    fetchPerformance();

    // Set up intervals
    const statusInterval = setInterval(fetchSystemStatus, 30000); // Every 30 seconds
    const performanceInterval = setInterval(fetchPerformance, 10000); // Every 10 seconds

    return () => {
      clearInterval(statusInterval);
      clearInterval(performanceInterval);
    };
  }, []);

  const getStatusColor = (status) => {
    return status === 'online' ? '#00ff41' : '#ff0040';
  };

  return (
    <div className="sidebar">
      {/* System Status */}
      <div className="system-status">
        <h3>System Status</h3>
        <div className="status-items">
          <div className="status-item">
            <div className="status-dot" style={{ backgroundColor: getStatusColor(systemStatus.dataRetriever) }}></div>
            <span>Data Retriever</span>
          </div>
          <div className="status-item">
            <div className="status-dot" style={{ backgroundColor: getStatusColor(systemStatus.logicEngine) }}></div>
            <span>Logic Engine</span>
          </div>
          <div className="status-item">
            <div className="status-dot" style={{ backgroundColor: getStatusColor(systemStatus.executor) }}></div>
            <span>Executor</span>
          </div>
        </div>
      </div>

      {/* System Metrics */}
      <div className="system-metrics">
        <h3>System Metrics</h3>
        <div className="metric-items">
          <div className="metric-item">
            <span className="metric-label">Uptime</span>
            <span className="metric-value">{systemMetrics.uptime}</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Memory</span>
            <span className="metric-value">{systemMetrics.memory}</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">CPU</span>
            <span className="metric-value">{systemMetrics.cpu}</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Total Trades</span>
            <span className="metric-value">{systemMetrics.trades}</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button className="action-btn">
            View Logs
          </button>
          <button className="action-btn">
            Export Data
          </button>
          <button className="action-btn">
            Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
