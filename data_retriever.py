"""
TradeX V3 - Data Retriever Module
Fetches historical and live BTC prices via Binance API
Computes technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
"""

import pandas as pd
import numpy as np
import ta
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
from datetime import datetime, timedelta
from config import Config

class DataRetriever:
    def __init__(self):
        """Initialize Data Retriever with Binance client"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Binance client
        if self.config.BINANCE_TESTNET:
            self.client = Client(
                self.config.BINANCE_API_KEY, 
                self.config.BINANCE_SECRET_KEY,
                testnet=True
            )
        else:
            self.client = Client(
                self.config.BINANCE_API_KEY, 
                self.config.BINANCE_SECRET_KEY
            )
        
        self.symbol = self.config.SYMBOL
        self.logger.info(f"Data Retriever initialized for {self.symbol}")
    
    def get_historical_data(self, hours=24):
        """Fetch historical BTC price data"""
        try:
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Fetch klines (candlestick data)
            klines = self.client.get_historical_klines(
                self.symbol,
                Client.KLINE_INTERVAL_1HOUR,
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert price columns to float
            price_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in price_columns:
                df[col] = df[col].astype(float)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            self.logger.info(f"Retrieved {len(df)} historical data points")
            return df
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return None
    
    def get_current_price(self):
        """Get current BTC price"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Error fetching current price: {e}")
            return None
    
    def get_24h_stats(self):
        """Get 24-hour statistics"""
        try:
            stats = self.client.get_ticker(symbol=self.symbol)
            return {
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'volume': float(stats['volume']),
                'quote_volume': float(stats['quoteVolume']),
                'high_24h': float(stats['highPrice']),
                'low_24h': float(stats['lowPrice']),
                'count': int(stats['count'])
            }
        except Exception as e:
            self.logger.error(f"Error fetching 24h stats: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate technical indicators"""
        try:
            if df is None or df.empty:
                return None
            
            # Create a copy to avoid modifying original data
            df_indicators = df.copy()
            
            # RSI
            df_indicators['rsi'] = ta.momentum.RSIIndicator(
                df_indicators['close'], 
                window=self.config.RSI_PERIOD
            ).rsi()
            
            # MACD
            macd = ta.trend.MACD(
                df_indicators['close'],
                window_fast=self.config.MACD_FAST,
                window_slow=self.config.MACD_SLOW,
                window_sign=self.config.MACD_SIGNAL
            )
            df_indicators['macd'] = macd.macd()
            df_indicators['macd_signal'] = macd.macd_signal()
            df_indicators['macd_histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(
                df_indicators['close'],
                window=self.config.BOLLINGER_PERIOD,
                window_dev=self.config.BOLLINGER_STD
            )
            df_indicators['bb_upper'] = bollinger.bollinger_hband()
            df_indicators['bb_middle'] = bollinger.bollinger_mavg()
            df_indicators['bb_lower'] = bollinger.bollinger_lband()
            df_indicators['bb_width'] = bollinger.bollinger_wband()
            df_indicators['bb_percent'] = bollinger.bollinger_pband()
            
            # Moving Averages
            for period in self.config.SMA_PERIODS:
                df_indicators[f'sma_{period}'] = ta.trend.SMAIndicator(
                    df_indicators['close'], 
                    window=period
                ).sma_indicator()
            
            # Volume indicators
            df_indicators['volume_sma'] = ta.trend.SMAIndicator(
                df_indicators['volume'], 
                window=20
            ).sma_indicator()
            
            # Price position relative to Bollinger Bands
            df_indicators['bb_position'] = (
                (df_indicators['close'] - df_indicators['bb_lower']) / 
                (df_indicators['bb_upper'] - df_indicators['bb_lower'])
            )
            
            # Advanced Indicators
            # Stochastic
            stoch = ta.momentum.StochasticOscillator(
                df_indicators['high'], df_indicators['low'], df_indicators['close'], 
                window=self.config.STOCHASTIC_K, 
                smooth_window=self.config.STOCHASTIC_D
            )
            df_indicators['stoch_k'] = stoch.stoch()
            df_indicators['stoch_d'] = stoch.stoch_signal()
            
            # Williams %R
            df_indicators['williams_r'] = ta.momentum.WilliamsRIndicator(
                df_indicators['high'], df_indicators['low'], df_indicators['close'], 
                window=self.config.WILLIAMS_R_PERIOD
            ).williams_r()
            
            # CCI (Commodity Channel Index)
            df_indicators['cci'] = ta.trend.CCIIndicator(
                df_indicators['high'], df_indicators['low'], df_indicators['close'], 
                window=self.config.CCI_PERIOD
            ).cci()
            
            # ADX (Average Directional Index)
            adx = ta.trend.ADXIndicator(
                df_indicators['high'], df_indicators['low'], df_indicators['close'], 
                window=self.config.ADX_PERIOD
            )
            df_indicators['adx'] = adx.adx()
            df_indicators['adx_pos'] = adx.adx_pos()
            df_indicators['adx_neg'] = adx.adx_neg()
            
            # ATR (Average True Range)
            df_indicators['atr'] = ta.volatility.AverageTrueRange(
                df_indicators['high'], df_indicators['low'], df_indicators['close'], 
                window=self.config.ATR_PERIOD
            ).average_true_range()
            
            # Volume Analysis
            df_indicators['volume_ratio'] = df_indicators['volume'] / df_indicators['volume_sma']
            df_indicators['volume_trend'] = df_indicators['volume'].pct_change()
            
            # Price Action Patterns
            df_indicators['price_trend'] = df_indicators['close'].pct_change()
            df_indicators['price_acceleration'] = df_indicators['price_trend'].diff()
            df_indicators['volatility'] = df_indicators['close'].rolling(window=20).std()
            
            # Support and Resistance Levels
            df_indicators['support_level'] = df_indicators['low'].rolling(window=20).min()
            df_indicators['resistance_level'] = df_indicators['high'].rolling(window=20).max()
            
            self.logger.info("Technical indicators calculated successfully")
            return df_indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {e}")
            return None
    
    def get_market_data(self):
        """Get comprehensive market data with indicators"""
        try:
            # Get historical data
            df = self.get_historical_data(hours=self.config.ML_LOOKBACK_HOURS)
            if df is None:
                return None
            
            # Calculate technical indicators
            df_with_indicators = self.calculate_technical_indicators(df)
            if df_with_indicators is None:
                return None
            
            # Get current price and 24h stats
            current_price = self.get_current_price()
            stats_24h = self.get_24h_stats()
            
            # Create market data dictionary
            market_data = {
                'dataframe': df_with_indicators,
                'current_price': current_price,
                'stats_24h': stats_24h,
                'timestamp': datetime.now(),
                'symbol': self.symbol
            }
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None
    
    def get_latest_indicators(self):
        """Get latest technical indicator values"""
        try:
            market_data = self.get_market_data()
            if market_data is None or market_data['dataframe'].empty:
                return None
            
            df = market_data['dataframe']
            latest = df.iloc[-1]
            
            indicators = {
                'rsi': latest['rsi'],
                'macd': latest['macd'],
                'macd_signal': latest['macd_signal'],
                'macd_histogram': latest['macd_histogram'],
                'bb_position': latest['bb_position'],
                'bb_width': latest['bb_width'],
                'price_trend': latest['price_trend'],
                'volume_trend': latest['volume_trend'],
                'current_price': market_data['current_price']
            }
            
            # Add moving averages
            for period in self.config.SMA_PERIODS:
                indicators[f'sma_{period}'] = latest[f'sma_{period}']
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error getting latest indicators: {e}")
            return None
