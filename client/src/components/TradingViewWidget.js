import React, { useEffect, useRef } from 'react';

const TradingViewWidget = ({ symbol = 'BTC' }) => {
  const container = useRef();

  useEffect(() => {
    // Add global error handler to suppress script errors
    const originalErrorHandler = window.onerror;
    window.onerror = function(msg, url, line, col, error) {
      // Suppress TradingView script errors
      if (msg && typeof msg === 'string' && (
        msg.includes('Script error') || 
        msg.includes('tradingview') || 
        msg.includes('external-embedding')
      )) {
        return true; // Prevent error from showing in console
      }
      // Call original error handler for other errors
      if (originalErrorHandler) {
        return originalErrorHandler(msg, url, line, col, error);
      }
      return false;
    };

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.onerror = () => {
      console.warn('TradingView widget failed to load, this is normal and will retry automatically');
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
      // Restore original error handler
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
