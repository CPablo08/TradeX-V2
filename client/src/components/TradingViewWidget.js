import React, { useEffect, useRef } from 'react';

const TradingViewWidget = ({ symbol = 'BTC' }) => {
  const container = useRef();

  useEffect(() => {
    // Comprehensive error suppression for TradingView
    const originalConsoleError = console.error;
    const originalConsoleWarn = console.warn;
    const originalErrorHandler = window.onerror;
    
    // Override console methods
    console.error = function(...args) {
      const message = args.join(' ');
      if (message.includes('Script error') || 
          message.includes('tradingview') || 
          message.includes('external-embedding') ||
          message.includes('bundle.js')) {
        return; // Suppress
      }
      originalConsoleError.apply(console, args);
    };
    
    console.warn = function(...args) {
      const message = args.join(' ');
      if (message.includes('Script error') || 
          message.includes('tradingview') || 
          message.includes('external-embedding')) {
        return; // Suppress
      }
      originalConsoleWarn.apply(console, args);
    };

    // Override window error handler
    window.onerror = function(msg, url, line, col, error) {
      if (msg && typeof msg === 'string' && (
        msg.includes('Script error') || 
        msg.includes('tradingview') || 
        msg.includes('external-embedding') ||
        msg.includes('bundle.js')
      )) {
        return true; // Suppress
      }
      if (originalErrorHandler) {
        return originalErrorHandler(msg, url, line, col, error);
      }
      return false;
    };

    // Create script with error handling
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.onerror = () => {
      // Silent error handling
    };
    script.onload = () => {
      // Silent success
    };
    
    script.innerHTML = `
      {
        "autosize": true,
        "symbol": "COINBASE:${symbol}USD",
        "interval": "1",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "enable_publishing": false,
        "hide_top_toolbar": false,
        "hide_legend": false,
        "save_image": false,
        "backgroundColor": "rgba(26, 28, 31, 1)",
        "gridColor": "rgba(255, 255, 255, 0.1)",
        "width": "100%",
        "height": "100%",
        "support_host": "https://www.tradingview.com"
      }`;
    
    const currentContainer = container.current;
    if (currentContainer) {
      currentContainer.innerHTML = '';
      currentContainer.appendChild(script);
    }

    return () => {
      // Restore original handlers
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
      window.onerror = originalErrorHandler;
      if (currentContainer) {
        currentContainer.innerHTML = '';
      }
    };
  }, [symbol]);

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: '100%', width: '100%' }}>
      <div className="tradingview-widget-container__widget" style={{ height: '100%', width: '100%' }}></div>
    </div>
  );
};

export default TradingViewWidget;
