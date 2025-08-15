#!/usr/bin/env python3
"""
Alpaca Data Collector
Handles fetching real-time and historical data from Alpaca Markets
"""

import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from loguru import logger
import ta
from config import Config

class AlpacaDataCollector:
    def __init__(self):
        self.api_key = Config.ALPACA_API_KEY
        self.secret_key = Config.ALPACA_SECRET_KEY
        self.base_url = Config.ALPACA_BASE_URL
        self.data_url = Config.ALPACA_DATA_BASE_URL
        self.paper_trading = Config.ALPACA_PAPER_TRADING
        
        # Headers for API requests
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }
        
        logger.info(f"🔗 Alpaca Data Collector initialized")
        logger.info(f"📊 Paper Trading: {self.paper_trading}")
        logger.info(f"🌐 Base URL: {self.base_url}")
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated request to Alpaca API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=Config.API_TIMEOUT)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=Config.API_TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return None
    
    def get_account_info(self):
        """Get account information"""
        try:
            account_data = self._make_request('GET', '/v2/account')
            if account_data:
                logger.info(f"✅ Account info retrieved")
                logger.info(f"💰 Cash: ${account_data.get('cash', 0)}")
                logger.info(f"📈 Portfolio Value: ${account_data.get('portfolio_value', 0)}")
                return account_data
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get account info: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions_data = self._make_request('GET', '/v2/positions')
            if positions_data:
                logger.info(f"✅ Positions retrieved: {len(positions_data)} positions")
                return positions_data
            return []
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            return []
    
    def get_historical_data(self, symbol, timeframe='1Hour', limit=100):
        """
        Get historical market data
        timeframe: 1Min, 5Min, 15Min, 30Min, 1Hour, 1Day
        """
        try:
            # Convert symbol format (BTC/USD -> BTCUSD)
            alpaca_symbol = symbol.replace('/', '')
            
            # Calculate start time (limit * timeframe)
            end_time = datetime.now()
            if timeframe == '1Min':
                start_time = end_time - timedelta(minutes=limit)
            elif timeframe == '5Min':
                start_time = end_time - timedelta(minutes=limit * 5)
            elif timeframe == '15Min':
                start_time = end_time - timedelta(minutes=limit * 15)
            elif timeframe == '30Min':
                start_time = end_time - timedelta(minutes=limit * 30)
            elif timeframe == '1Hour':
                start_time = end_time - timedelta(hours=limit)
            elif timeframe == '1Day':
                start_time = end_time - timedelta(days=limit)
            else:
                start_time = end_time - timedelta(hours=limit)
            
            params = {
                'symbols': alpaca_symbol,
                'timeframe': timeframe,
                'start': start_time.isoformat() + 'Z',
                'end': end_time.isoformat() + 'Z',
                'limit': limit
            }
            
            # Use data API for historical data
            url = f"{self.data_url}/v2/stocks/{alpaca_symbol}/bars"
            response = requests.get(url, headers=self.headers, params=params, timeout=Config.API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if 'bars' in data and alpaca_symbol in data['bars']:
                bars = data['bars'][alpaca_symbol]
                
                # Convert to DataFrame
                df = pd.DataFrame(bars)
                df['timestamp'] = pd.to_datetime(df['t'])
                df.set_index('timestamp', inplace=True)
                
                # Rename columns to match expected format
                df.rename(columns={
                    'o': 'open',
                    'h': 'high',
                    'l': 'low',
                    'c': 'close',
                    'v': 'volume',
                    'n': 'trade_count',
                    'vw': 'vwap'
                }, inplace=True)
                
                logger.info(f"✅ Historical data retrieved for {symbol}: {len(df)} bars")
                return df
            
            logger.warning(f"⚠️ No data returned for {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_latest_price(self, symbol):
        """Get latest price for a symbol"""
        try:
            # Convert symbol format (BTC/USD -> BTCUSD)
            alpaca_symbol = symbol.replace('/', '')
            
            # Use data API for latest price
            url = f"{self.data_url}/v2/stocks/{alpaca_symbol}/trades/latest"
            response = requests.get(url, headers=self.headers, timeout=Config.API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if 'trade' in data:
                price = data['trade']['p']
                logger.info(f"✅ Latest price for {symbol}: ${price}")
                return price
            
            logger.warning(f"⚠️ No price data for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get latest price for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators for the data"""
        if df.empty:
            return df
        
        try:
            # Basic indicators
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['macd_signal'] = ta.trend.macd_signal(df['close'])
            df['macd_histogram'] = ta.trend.macd_diff(df['close'])
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = bb.bollinger_wband()
            df['bb_percent'] = bb.bollinger_pband()
            
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            # ATR (Average True Range)
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Williams %R
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # CCI (Commodity Channel Index)
            df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'])
            
            # ADX (Average Directional Index)
            df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'])
            
            # VWAP
            df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
            
            logger.info(f"✅ Technical indicators calculated: {len(df.columns)} features")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate technical indicators: {e}")
            return df
    
    def identify_chart_patterns(self, df):
        """Identify chart patterns in the data"""
        if df.empty:
            return {}
        
        patterns = {}
        
        try:
            # Simple pattern detection
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            
            # Double Top/Bottom detection
            if len(close_prices) >= 20:
                # Look for double top
                peaks = []
                for i in range(1, len(close_prices) - 1):
                    if close_prices[i] > close_prices[i-1] and close_prices[i] > close_prices[i+1]:
                        peaks.append((i, close_prices[i]))
                
                if len(peaks) >= 2:
                    # Check if peaks are similar in height
                    peak1, peak2 = peaks[-2], peaks[-1]
                    if abs(peak1[1] - peak2[1]) / peak1[1] < 0.02:  # 2% tolerance
                        patterns['double_top'] = True
                        patterns['double_top_price'] = peak1[1]
            
            # Support and Resistance levels
            if len(close_prices) >= 50:
                recent_highs = high_prices[-20:]
                recent_lows = low_prices[-20:]
                
                resistance = np.percentile(recent_highs, 90)
                support = np.percentile(recent_lows, 10)
                
                patterns['resistance_level'] = resistance
                patterns['support_level'] = support
                patterns['current_price'] = close_prices[-1]
                patterns['price_position'] = (close_prices[-1] - support) / (resistance - support)
            
            # Trend detection
            if len(close_prices) >= 20:
                sma_20 = df['sma_20'].iloc[-1]
                sma_50 = df['sma_50'].iloc[-1]
                current_price = close_prices[-1]
                
                if current_price > sma_20 > sma_50:
                    patterns['trend'] = 'uptrend'
                elif current_price < sma_20 < sma_50:
                    patterns['trend'] = 'downtrend'
                else:
                    patterns['trend'] = 'sideways'
            
            logger.info(f"✅ Chart patterns identified: {len(patterns)} patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to identify chart patterns: {e}")
            return {}
    
    def get_market_data(self, symbol, lookback_hours=24):
        """Get comprehensive market data for a symbol"""
        try:
            # Get historical data
            df = self.get_historical_data(symbol, timeframe='1Hour', limit=lookback_hours)
            
            if df.empty:
                logger.warning(f"⚠️ No data available for {symbol}")
                return None
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Identify chart patterns
            patterns = self.identify_chart_patterns(df)
            
            # Get latest price
            latest_price = self.get_latest_price(symbol)
            
            market_data = {
                'symbol': symbol,
                'data': df,
                'patterns': patterns,
                'latest_price': latest_price,
                'timestamp': datetime.now()
            }
            
            logger.info(f"✅ Market data collected for {symbol}")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get market data for {symbol}: {e}")
            return None
