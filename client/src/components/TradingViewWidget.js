import React, { useEffect, useRef } from 'react';

const TradingViewWidget = () => {
  const btcContainer = useRef();
  const ethContainer = useRef();

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    
    script.onload = () => {
      if (window.TradingView) {
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
      }
    };
    
    if (btcContainer.current) {
      btcContainer.current.appendChild(script);
    }

    return () => {
      if (btcContainer.current) {
        btcContainer.current.innerHTML = '';
      }
      if (ethContainer.current) {
        ethContainer.current.innerHTML = '';
      }
    };
  }, []);

  return (
    <div className="tradingview-container">
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
