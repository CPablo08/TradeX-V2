import React, { useEffect, useRef, useState } from 'react';

const TradingViewWidget = () => {
  const btcContainer = useRef();
  const ethContainer = useRef();
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [scriptError, setScriptError] = useState(false);

  useEffect(() => {
    // Check if script is already loaded
    if (window.TradingView) {
      setScriptLoaded(true);
      return;
    }

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    
    script.onload = () => {
      console.log('TradingView script loaded successfully');
      setScriptLoaded(true);
      setScriptError(false);
    };

    script.onerror = () => {
      console.error('Failed to load TradingView script');
      setScriptError(true);
      setScriptLoaded(false);
    };
    
    // Add script to document head instead of container
    document.head.appendChild(script);

    return () => {
      // Clean up script if component unmounts
      const existingScript = document.querySelector('script[src="https://s3.tradingview.com/tv.js"]');
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, []);

  useEffect(() => {
    if (!scriptLoaded || !window.TradingView) return;

    try {
      // BTC Widget
      if (btcContainer.current) {
        new window.TradingView.widget({
          width: "100%",
          height: "100%",
          symbol: "COINBASE:BTCUSD",
          interval: "D",
          timezone: "Etc/UTC",
          theme: "dark",
          style: "1",
          locale: "en",
          toolbar_bg: "#1A1C1F",
          enable_publishing: false,
          allow_symbol_change: false,
          container_id: "tradingview_btc_widget",
          studies: [],
          disabled_features: [
            "use_localstorage_for_settings",
            "volume_force_overlay",
            "show_chart_property_page",
            "header_symbol_search",
            "header_compare",
            "header_settings",
            "header_fullscreen_button",
            "header_screenshot",
            "header_indicators",
            "header_undo_redo",
            "header_saveload"
          ],
          enabled_features: [
            "study_templates"
          ],
          overrides: {
            "paneProperties.background": "#1A1C1F",
            "paneProperties.vertGridProperties.color": "#2A2D30",
            "paneProperties.horzGridProperties.color": "#2A2D30",
            "symbolWatermarkProperties.transparency": 90,
            "scalesProperties.textColor": "#ffffff",
            "scalesProperties.backgroundColor": "#1A1C1F"
          },
          loading_screen: {
            backgroundColor: "#1A1C1F",
            foregroundColor: "#ffffff"
          }
        });
      }

      // ETH Widget
      if (ethContainer.current) {
        new window.TradingView.widget({
          width: "100%",
          height: "100%",
          symbol: "COINBASE:ETHUSD",
          interval: "D",
          timezone: "Etc/UTC",
          theme: "dark",
          style: "1",
          locale: "en",
          toolbar_bg: "#1A1C1F",
          enable_publishing: false,
          allow_symbol_change: false,
          container_id: "tradingview_eth_widget",
          studies: [],
          disabled_features: [
            "use_localstorage_for_settings",
            "volume_force_overlay",
            "show_chart_property_page",
            "header_symbol_search",
            "header_compare",
            "header_settings",
            "header_fullscreen_button",
            "header_screenshot",
            "header_indicators",
            "header_undo_redo",
            "header_saveload"
          ],
          enabled_features: [
            "study_templates"
          ],
          overrides: {
            "paneProperties.background": "#1A1C1F",
            "paneProperties.vertGridProperties.color": "#2A2D30",
            "paneProperties.horzGridProperties.color": "#2A2D30",
            "symbolWatermarkProperties.transparency": 90,
            "scalesProperties.textColor": "#ffffff",
            "scalesProperties.backgroundColor": "#1A1C1F"
          },
          loading_screen: {
            backgroundColor: "#1A1C1F",
            foregroundColor: "#ffffff"
          }
        });
      }
    } catch (error) {
      console.error('Error creating TradingView widgets:', error);
      setScriptError(true);
    }
  }, [scriptLoaded]);

  return (
    <div className="tradingview-container">
      {scriptError && (
        <div style={{ 
          color: '#ff6b6b', 
          textAlign: 'center', 
          padding: '20px',
          backgroundColor: '#2a2d30',
          borderRadius: '8px',
          margin: '10px'
        }}>
          ⚠️ TradingView charts failed to load. Please check your internet connection.
        </div>
      )}
      
      {!scriptLoaded && !scriptError && (
        <div style={{ 
          color: '#ffffff', 
          textAlign: 'center', 
          padding: '20px',
          backgroundColor: '#2a2d30',
          borderRadius: '8px',
          margin: '10px'
        }}>
          📊 Loading TradingView charts...
        </div>
      )}
      
      <div className="charts-grid">
        <div className="chart-item">
          <div className="chart-label">BTC/USD</div>
          <div 
            ref={btcContainer} 
            style={{ 
              width: '100%', 
              height: '100%', 
              flex: 1,
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <div 
              id="tradingview_btc_widget" 
              style={{ 
                width: '100%', 
                height: '100%'
              }}
            ></div>
          </div>
        </div>
        
        <div className="chart-item">
          <div className="chart-label">ETH/USD</div>
          <div 
            ref={ethContainer} 
            style={{ 
              width: '100%', 
              height: '100%', 
              flex: 1,
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <div 
              id="tradingview_eth_widget" 
              style={{ 
                width: '100%', 
                height: '100%'
              }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingViewWidget;
