#!/usr/bin/env python3
"""
Test Data Collector for TradeX
Generates realistic mock data for testing the trading system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class TestDataCollector:
    def __init__(self):
        self.base_prices = {
            'BTC-USD': 45000,
            'ETH-USD': 2800
        }
        
    def generate_mock_data(self, symbol, lookback_days=30):
        """Generate realistic mock OHLCV data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Generate hourly timestamps
        timestamps = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Base price for the symbol
        base_price = self.base_prices.get(symbol, 1000)
        
        # Generate realistic price movements
        np.random.seed(42)  # For reproducible results
        
        # Start with base price
        prices = [base_price]
        
        # Generate price movements with some volatility
        for i in range(len(timestamps) - 1):
            # Random price change between -2% and +2%
            change_pct = np.random.normal(0, 0.01)  # 1% standard deviation
            new_price = prices[-1] * (1 + change_pct)
            prices.append(max(new_price, base_price * 0.5))  # Don't go below 50% of base
        
        # Create OHLCV data
        data = []
        for i, timestamp in enumerate(timestamps):
            price = prices[i]
            
            # Generate OHLC from close price
            volatility = price * 0.02  # 2% volatility
            
            open_price = price + np.random.normal(0, volatility * 0.1)
            high_price = price + abs(np.random.normal(0, volatility * 0.5))
            low_price = price - abs(np.random.normal(0, volatility * 0.5))
            close_price = price
            
            # Ensure OHLC relationship
            high_price = max(open_price, high_price, close_price)
            low_price = min(open_price, low_price, close_price)
            
            # Generate volume (higher volume with larger price movements)
            base_volume = 1000000  # Base volume
            price_change = abs(close_price - open_price) / open_price
            volume = base_volume * (1 + price_change * 10) * np.random.uniform(0.5, 2.0)
            
            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def fetch_historical_data(self, symbol, granularity='1H', lookback_days=30):
        """Mock historical data fetch"""
        return self.generate_mock_data(symbol, lookback_days)
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators on the mock data"""
        try:
            # Simple moving averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # Exponential moving averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            df['atr'] = true_range.rolling(window=14).mean()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price action features
            df['price_change'] = df['close'].pct_change()
            df['high_low_ratio'] = df['high'] / df['low']
            df['body_size'] = abs(df['close'] - df['open']) / df['open']
            
            # Support and resistance (simplified)
            df['support_level'] = df['low'].rolling(window=20).min()
            df['resistance_level'] = df['high'].rolling(window=20).max()
            df['distance_to_support'] = (df['close'] - df['support_level']) / df['close']
            df['distance_to_resistance'] = (df['resistance_level'] - df['close']) / df['close']
            
            # Trend features
            df['higher_high'] = df['high'] > df['high'].shift(1)
            df['lower_low'] = df['low'] < df['low'].shift(1)
            df['higher_close'] = df['close'] > df['close'].shift(1)
            
            # Volatility
            df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            return df
            
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return df
    
    def identify_chart_patterns(self, df):
        """Mock chart pattern identification"""
        patterns = {}
        
        # Simple pattern detection based on price action
        if len(df) > 20:
            recent_data = df.tail(20)
            
            # Double top pattern (simplified)
            highs = recent_data['high'].nlargest(3)
            if len(highs) >= 2:
                high1, high2 = highs.iloc[0], highs.iloc[1]
                if abs(high1 - high2) / high1 < 0.02:  # Within 2%
                    patterns['double_top'] = True
            
            # Double bottom pattern (simplified)
            lows = recent_data['low'].nsmallest(3)
            if len(lows) >= 2:
                low1, low2 = lows.iloc[0], lows.iloc[1]
                if abs(low1 - low2) / low1 < 0.02:  # Within 2%
                    patterns['double_bottom'] = True
            
            # Trend patterns
            if recent_data['sma_20'].iloc[-1] > recent_data['sma_50'].iloc[-1]:
                patterns['uptrend'] = True
            else:
                patterns['downtrend'] = True
        
        return patterns
    
    def get_market_data(self, symbol):
        """Get complete market data with indicators and patterns"""
        df = self.fetch_historical_data(symbol)
        df = self.calculate_technical_indicators(df)
        patterns = self.identify_chart_patterns(df)
        
        return df, patterns

if __name__ == "__main__":
    # Test the data collector
    collector = TestDataCollector()
    
    # Generate test data
    df, patterns = collector.get_market_data('BTC-USD')
    
    print(f"Generated {len(df)} data points")
    print(f"Patterns detected: {patterns}")
    print(f"Latest price: ${df['close'].iloc[-1]:.2f}")
    print(f"RSI: {df['rsi'].iloc[-1]:.2f}")
    print(f"Volume ratio: {df['volume_ratio'].iloc[-1]:.2f}")
