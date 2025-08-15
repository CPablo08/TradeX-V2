#!/usr/bin/env python3
"""
Data Collector for TradeX
Fetches market data from Coinbase Advanced Trade API
"""

import pandas as pd
import numpy as np
import requests
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from loguru import logger
from config import Config

class DataCollector:
    def __init__(self):
        self.api_key_name = Config.CB_API_KEY_NAME
        self.private_key = Config.CB_PRIVATE_KEY
        self.base_url = "https://api.coinbase.com/api/v3/brokerage"
        
    def _get_signature(self, timestamp, method, request_path, body=''):
        """Generate Coinbase Advanced Trade API signature using private key"""
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.backends import default_backend
            
            # Load the private key
            private_key = serialization.load_pem_private_key(
                self.private_key.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            
            # Create the message to sign
            message = timestamp + method + request_path + body
            
            # Sign the message
            signature = private_key.sign(
                message.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            
            # Return base64 encoded signature
            return base64.b64encode(signature).decode('utf-8')
            
        except ImportError:
            # Fallback to HMAC if cryptography not available
            logger.warning("cryptography library not available, using HMAC fallback")
            message = timestamp + method + request_path + body
            # Extract the key from the PEM format
            key_lines = self.private_key.split('\n')
            key_data = ''.join([line for line in key_lines if line and not line.startswith('-----')])
            key_bytes = base64.b64decode(key_data)
            
            signature = hmac.new(
                key_bytes,
                message.encode('utf-8'),
                hashlib.sha256
            )
            return base64.b64encode(signature.digest()).decode('utf-8')
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to Coinbase API"""
        try:
            url = f"{self.base_url}{endpoint}"
            timestamp = str(int(time.time()))
            
            # Prepare request
            if params:
                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                url += f"?{query_string}"
            
            body = json.dumps(data) if data else ''
            
            # Generate headers for Advanced Trade API
            signature = self._get_signature(timestamp, method, endpoint, body)
            
            headers = {
                'CB-ACCESS-KEY': self.api_key_name,
                'CB-ACCESS-SIGN': signature,
                'CB-ACCESS-TIMESTAMP': timestamp,
                'Content-Type': 'application/json'
            }
            
            # Make request
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def fetch_historical_data(self, symbol, granularity='1H', lookback_days=30):
        """Fetch historical OHLCV data from Coinbase"""
        try:
            logger.info(f"Fetching historical data for {symbol}")
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(days=lookback_days)
            
            # Convert granularity to seconds
            granularity_map = {
                '1M': 60,
                '5M': 300,
                '15M': 900,
                '1H': 3600,
                '6H': 21600,
                '1D': 86400
            }
            
            granularity_seconds = granularity_map.get(granularity, 3600)
            
            # Prepare request parameters
            params = {
                'product_id': symbol,
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'granularity': granularity_seconds
            }
            
            # Make API request
            endpoint = "/products/candles"
            response = self._make_request('GET', endpoint, params)
            
            if not response or 'candles' not in response:
                logger.error(f"No data received for {symbol}")
                return None
            
            # Parse response
            candles = response['candles']
            data = []
            
            for candle in candles:
                data.append({
                    'timestamp': pd.to_datetime(candle['start']),
                    'open': float(candle['open']),
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'close': float(candle['close']),
                    'volume': float(candle['volume'])
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"Fetched {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators"""
        try:
            if df is None or len(df) < 50:
                return df
            
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Stochastic
            low_min = df['low'].rolling(window=14).min()
            high_max = df['high'].rolling(window=14).max()
            df['stoch'] = 100 * (df['close'] - low_min) / (high_max - low_min)
            df['stoch_signal'] = df['stoch'].rolling(window=3).mean()
            
            # Williams %R
            df['williams_r'] = -100 * (high_max - df['close']) / (high_max - low_min)
            
            # CCI (Commodity Channel Index)
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            sma_tp = typical_price.rolling(window=20).mean()
            mad = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())))
            df['cci'] = (typical_price - sma_tp) / (0.015 * mad)
            
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
            
            # ADX (Average Directional Index)
            plus_dm = df['high'].diff()
            minus_dm = df['low'].diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = abs(minus_dm)
            
            tr14 = true_range.rolling(window=14).mean()
            plus_di14 = 100 * (plus_dm.rolling(window=14).mean() / tr14)
            minus_di14 = 100 * (minus_dm.rolling(window=14).mean() / tr14)
            
            dx = 100 * abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)
            df['adx'] = dx.rolling(window=14).mean()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # OBV (On-Balance Volume)
            df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
            
            # VWAP (Volume Weighted Average Price)
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            # Price action features
            df['price_change'] = df['close'].pct_change()
            df['price_change_5'] = df['close'].pct_change(5)
            df['price_change_10'] = df['close'].pct_change(10)
            df['price_change_20'] = df['close'].pct_change(20)
            
            df['high_low_ratio'] = df['high'] / df['low']
            df['body_size'] = abs(df['close'] - df['open']) / df['open']
            df['upper_shadow'] = (df['high'] - np.maximum(df['open'], df['close'])) / df['open']
            df['lower_shadow'] = (np.minimum(df['open'], df['close']) - df['low']) / df['open']
            
            # Support and Resistance levels
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
            df['volatility_ratio'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
            
            # Trend strength
            df['trend_strength'] = abs(df['sma_20'] - df['sma_50']) / df['sma_50']
            
            # Fill NaN values
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    def identify_chart_patterns(self, df):
        """Identify chart patterns"""
        patterns = {}
        
        try:
            if df is None or len(df) < 50:
                return patterns
            
            # Get recent data for pattern detection
            recent_data = df.tail(50)
            
            # Double Top Pattern
            patterns['double_top'] = self._detect_double_top(recent_data)
            
            # Double Bottom Pattern
            patterns['double_bottom'] = self._detect_double_bottom(recent_data)
            
            # Head and Shoulders Pattern
            patterns['head_shoulders'] = self._detect_head_shoulders(recent_data)
            
            # Inverse Head and Shoulders Pattern
            patterns['inverse_head_shoulders'] = self._detect_inverse_head_shoulders(recent_data)
            
            # Triangle Patterns
            patterns['ascending_triangle'] = self._detect_ascending_triangle(recent_data)
            patterns['descending_triangle'] = self._detect_descending_triangle(recent_data)
            patterns['symmetrical_triangle'] = self._detect_symmetrical_triangle(recent_data)
            
            # Flag Patterns
            patterns['bull_flag'] = self._detect_bull_flag(recent_data)
            patterns['bear_flag'] = self._detect_bear_flag(recent_data)
            
            # Cup and Handle Pattern
            patterns['cup_handle'] = self._detect_cup_handle(recent_data)
            
        except Exception as e:
            logger.error(f"Error identifying chart patterns: {e}")
        
        return patterns
    
    def _detect_double_top(self, df):
        """Detect double top pattern"""
        try:
            highs = df['high'].nlargest(5)
            if len(highs) >= 2:
                high1, high2 = highs.iloc[0], highs.iloc[1]
                # Check if highs are within 2% of each other
                if abs(high1 - high2) / high1 < 0.02:
                    return True
        except:
            pass
        return False
    
    def _detect_double_bottom(self, df):
        """Detect double bottom pattern"""
        try:
            lows = df['low'].nsmallest(5)
            if len(lows) >= 2:
                low1, low2 = lows.iloc[0], lows.iloc[1]
                # Check if lows are within 2% of each other
                if abs(low1 - low2) / low1 < 0.02:
                    return True
        except:
            pass
        return False
    
    def _detect_head_shoulders(self, df):
        """Detect head and shoulders pattern"""
        # Simplified detection
        return False
    
    def _detect_inverse_head_shoulders(self, df):
        """Detect inverse head and shoulders pattern"""
        # Simplified detection
        return False
    
    def _detect_ascending_triangle(self, df):
        """Detect ascending triangle pattern"""
        # Simplified detection
        return False
    
    def _detect_descending_triangle(self, df):
        """Detect descending triangle pattern"""
        # Simplified detection
        return False
    
    def _detect_symmetrical_triangle(self, df):
        """Detect symmetrical triangle pattern"""
        # Simplified detection
        return False
    
    def _detect_bull_flag(self, df):
        """Detect bull flag pattern"""
        # Simplified detection
        return False
    
    def _detect_bear_flag(self, df):
        """Detect bear flag pattern"""
        # Simplified detection
        return False
    
    def _detect_cup_handle(self, df):
        """Detect cup and handle pattern"""
        # Simplified detection
        return False
    
    def get_market_data(self, symbol):
        """Get complete market data with indicators and patterns"""
        try:
            # Fetch historical data
            df = self.fetch_historical_data(symbol)
            if df is None:
                return None, {}
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Identify patterns
            patterns = self.identify_chart_patterns(df)
            
            return df, patterns
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None, {}
