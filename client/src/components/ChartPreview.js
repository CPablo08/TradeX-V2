import React, { useState, useEffect, useRef } from 'react';
import './ChartPreview.css';

const ChartPreview = ({ data, trades, strategy, symbol }) => {
  const canvasRef = useRef(null);
  const [chartType, setChartType] = useState('candlestick');
  const [timeframe, setTimeframe] = useState('1D');
  const [showSignals, setShowSignals] = useState(true);
  const [showVolume, setShowVolume] = useState(true);

  useEffect(() => {
    if (data && data.length > 0) {
      drawChart();
    }
  }, [data, trades, chartType, timeframe, showSignals, showVolume]);

  const drawChart = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#1a1c23';
    ctx.fillRect(0, 0, width, height);

    if (!data || data.length === 0) return;

    // Calculate chart dimensions
    const padding = 60;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const volumeHeight = showVolume ? 80 : 0;
    const priceHeight = chartHeight - volumeHeight;

    // Find price range
    const prices = data.map(d => [d.high, d.low, d.open, d.close]).flat();
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;

    // Find volume range
    const volumes = data.map(d => d.volume);
    const maxVolume = Math.max(...volumes);

    // Calculate scales
    const xScale = chartWidth / (data.length - 1);
    const yScale = priceHeight / priceRange;
    const volumeScale = volumeHeight / maxVolume;

    // Draw grid
    drawGrid(ctx, width, height, padding, data.length, minPrice, maxPrice);

    // Draw price chart
    if (chartType === 'candlestick') {
      drawCandlesticks(ctx, data, padding, xScale, yScale, minPrice);
    } else {
      drawLineChart(ctx, data, padding, xScale, yScale, minPrice);
    }

    // Draw volume
    if (showVolume) {
      drawVolume(ctx, data, padding, xScale, volumeScale, chartHeight - volumeHeight);
    }

    // Draw signals
    if (showSignals && trades) {
      drawSignals(ctx, trades, data, padding, xScale, yScale, minPrice);
    }

    // Draw labels
    drawLabels(ctx, width, height, padding, data, minPrice, maxPrice);
  };

  const drawGrid = (ctx, width, height, padding, dataLength, minPrice, maxPrice) => {
    ctx.strokeStyle = '#3a3d41';
    ctx.lineWidth = 1;

    // Vertical grid lines
    for (let i = 0; i <= 10; i++) {
      const x = padding + (width - padding * 2) * (i / 10);
      ctx.beginPath();
      ctx.moveTo(x, padding);
      ctx.lineTo(x, height - padding);
      ctx.stroke();
    }

    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = padding + (height - padding * 2) * (i / 5);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }
  };

  const drawCandlesticks = (ctx, data, padding, xScale, yScale, minPrice) => {
    data.forEach((candle, i) => {
      const x = padding + i * xScale;
      const openY = padding + (candle.open - minPrice) * yScale;
      const closeY = padding + (candle.close - minPrice) * yScale;
      const highY = padding + (candle.high - minPrice) * yScale;
      const lowY = padding + (candle.low - minPrice) * yScale;

      const isGreen = candle.close >= candle.open;
      ctx.strokeStyle = isGreen ? '#00ff88' : '#ff4757';
      ctx.fillStyle = isGreen ? '#00ff88' : '#ff4757';
      ctx.lineWidth = 2;

      // Draw wick
      ctx.beginPath();
      ctx.moveTo(x, highY);
      ctx.lineTo(x, lowY);
      ctx.stroke();

      // Draw body
      const bodyHeight = Math.max(1, Math.abs(closeY - openY));
      const bodyY = Math.min(openY, closeY);
      ctx.fillRect(x - 3, bodyY, 6, bodyHeight);
    });
  };

  const drawLineChart = (ctx, data, padding, xScale, yScale, minPrice) => {
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((point, i) => {
      const x = padding + i * xScale;
      const y = padding + (point.close - minPrice) * yScale;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();
  };

  const drawVolume = (ctx, data, padding, xScale, volumeScale, volumeY) => {
    ctx.fillStyle = '#8a8d91';
    
    data.forEach((candle, i) => {
      const x = padding + i * xScale;
      const volumeHeight = candle.volume * volumeScale;
      const y = volumeY + padding - volumeHeight;
      
      ctx.fillRect(x - 2, y, 4, volumeHeight);
    });
  };

  const drawSignals = (ctx, trades, data, padding, xScale, yScale, minPrice) => {
    trades.forEach(trade => {
      const dataIndex = data.findIndex(d => 
        d.date.toDateString() === trade.date.toDateString()
      );
      
      if (dataIndex !== -1) {
        const x = padding + dataIndex * xScale;
        const y = padding + (trade.price - minPrice) * yScale;

        if (trade.action === 'BUY') {
          // Draw buy signal (green triangle)
          ctx.fillStyle = '#00ff88';
          ctx.beginPath();
          ctx.moveTo(x, y - 10);
          ctx.lineTo(x - 8, y + 5);
          ctx.lineTo(x + 8, y + 5);
          ctx.closePath();
          ctx.fill();
        } else if (trade.action === 'SELL') {
          // Draw sell signal (red triangle)
          ctx.fillStyle = '#ff4757';
          ctx.beginPath();
          ctx.moveTo(x, y + 10);
          ctx.lineTo(x - 8, y - 5);
          ctx.lineTo(x + 8, y - 5);
          ctx.closePath();
          ctx.fill();
        }
      }
    });
  };

  const drawLabels = (ctx, width, height, padding, data, minPrice, maxPrice) => {
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Monaco, monospace';
    ctx.textAlign = 'center';

    // Price labels
    for (let i = 0; i <= 5; i++) {
      const price = minPrice + (maxPrice - minPrice) * (i / 5);
      const y = padding + (height - padding * 2) * (i / 5);
      ctx.fillText(`$${price.toFixed(2)}`, padding - 10, y + 4);
    }

    // Date labels
    ctx.textAlign = 'center';
    const dateStep = Math.max(1, Math.floor(data.length / 5));
    for (let i = 0; i < data.length; i += dateStep) {
      const x = padding + i * ((width - padding * 2) / (data.length - 1));
      const date = data[i].date.toLocaleDateString();
      ctx.fillText(date, x, height - padding + 20);
    }

    // Title
    ctx.font = '16px Monaco, monospace';
    ctx.fillText(`${symbol} Chart Preview`, width / 2, 20);
  };

  return (
    <div className="chart-preview">
      <div className="chart-controls">
        <div className="control-group">
          <label>Chart Type:</label>
          <select 
            value={chartType} 
            onChange={(e) => setChartType(e.target.value)}
            className="chart-select"
          >
            <option value="candlestick">Candlestick</option>
            <option value="line">Line</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>Timeframe:</label>
          <select 
            value={timeframe} 
            onChange={(e) => setTimeframe(e.target.value)}
            className="chart-select"
          >
            <option value="1D">1 Day</option>
            <option value="1W">1 Week</option>
            <option value="1M">1 Month</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showSignals}
              onChange={(e) => setShowSignals(e.target.checked)}
            />
            Show Signals
          </label>
        </div>
        
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showVolume}
              onChange={(e) => setShowVolume(e.target.checked)}
            />
            Show Volume
          </label>
        </div>
      </div>

      <div className="chart-container">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="chart-canvas"
        />
      </div>

      {data && data.length > 0 && (
        <div className="chart-info">
          <div className="info-item">
            <span>Data Points:</span>
            <span>{data.length}</span>
          </div>
          <div className="info-item">
            <span>Date Range:</span>
            <span>{data[0].date.toLocaleDateString()} - {data[data.length - 1].date.toLocaleDateString()}</span>
          </div>
          <div className="info-item">
            <span>Price Range:</span>
            <span>${Math.min(...data.map(d => d.low)).toFixed(2)} - ${Math.max(...data.map(d => d.high)).toFixed(2)}</span>
          </div>
          {trades && (
            <div className="info-item">
              <span>Signals:</span>
              <span>{trades.length}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChartPreview;
