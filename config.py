"""
TradeX V3 Configuration
Automated BTC Trading Platform Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Binance API Configuration
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # Binance API URLs (Testnet vs Live)
    BINANCE_TESTNET_URL = "https://testnet.binance.vision"
    BINANCE_LIVE_URL = "https://api.binance.com"
    BINANCE_WS_TESTNET_URL = "wss://testnet.binance.vision/ws"
    BINANCE_WS_LIVE_URL = "wss://stream.binance.com:9443/ws"
    
    # Select appropriate URLs based on testnet setting
    BINANCE_BASE_URL = BINANCE_TESTNET_URL if BINANCE_TESTNET else BINANCE_LIVE_URL
    BINANCE_WS_URL = BINANCE_WS_TESTNET_URL if BINANCE_TESTNET else BINANCE_WS_LIVE_URL
    
    # Trading Configuration
    SYMBOL = 'BTCUSDT'
    QUANTITY = 0.001  # Minimum BTC quantity
    MAX_QUANTITY = 0.01  # Maximum BTC quantity per trade
    
    # Technical Analysis Configuration
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    SMA_PERIODS = [20, 50, 200]
    
    # Multi-Timeframe Analysis
    TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    TIMEFRAME_WEIGHTS = {
        '1m': 0.05,   # 5% weight for noise filtering
        '5m': 0.15,   # 15% weight for short-term signals
        '15m': 0.25,  # 25% weight for medium-term trends
        '1h': 0.30,   # 30% weight for primary analysis
        '4h': 0.20,   # 20% weight for trend confirmation
        '1d': 0.05    # 5% weight for long-term context
    }
    
    # Advanced Indicators
    STOCHASTIC_K = 14
    STOCHASTIC_D = 3
    WILLIAMS_R_PERIOD = 14
    CCI_PERIOD = 20
    ADX_PERIOD = 14
    ATR_PERIOD = 14
    
    # ML Model Configuration
    ML_LOOKBACK_HOURS = 48  # Increased for better pattern recognition
    ML_PREDICTION_HORIZON = 1  # hours
    ML_CONFIDENCE_THRESHOLD = 0.75  # Increased for higher quality signals
    
    # Ensemble Learning
    ENSEMBLE_MODELS = True  # Use multiple models for better predictions
    MODEL_TYPES = ['LSTM', 'GRU', 'Transformer']  # Different model architectures
    ENSEMBLE_WEIGHTS = [0.4, 0.35, 0.25]  # Weight for each model type
    
    # Feature Engineering
    TECHNICAL_FEATURES = True  # Include technical indicators as features
    SENTIMENT_ANALYSIS = True  # Include market sentiment data
    VOLUME_ANALYSIS = True  # Include volume-based features
    MARKET_MICROSTRUCTURE = True  # Include order book data
    
    # Logic Engine Weights
    TECHNICAL_INDICATORS_WEIGHT = 0.30
    ML_PREDICTION_WEIGHT = 0.35
    TREND_CONFIRMATION_WEIGHT = 0.20
    LIQUIDITY_VOLATILITY_WEIGHT = 0.15
    
    # Market Regime Detection
    REGIME_DETECTION = True  # Detect market conditions (trending/ranging/volatile)
    REGIME_ADAPTATION = True  # Adapt strategy based on market regime
    VOLATILITY_REGIMES = ['LOW', 'MEDIUM', 'HIGH']
    TREND_REGIMES = ['BULLISH', 'BEARISH', 'SIDEWAYS']
    
    # Regime-Specific Parameters
    REGIME_PARAMETERS = {
        'BULLISH_LOW': {'position_size': 0.03, 'stop_loss': 1.5, 'take_profit': 6.0},
        'BULLISH_MEDIUM': {'position_size': 0.025, 'stop_loss': 2.0, 'take_profit': 5.0},
        'BULLISH_HIGH': {'position_size': 0.02, 'stop_loss': 2.5, 'take_profit': 4.0},
        'BEARISH_LOW': {'position_size': 0.02, 'stop_loss': 2.0, 'take_profit': 4.0},
        'BEARISH_MEDIUM': {'position_size': 0.025, 'stop_loss': 2.5, 'take_profit': 5.0},
        'BEARISH_HIGH': {'position_size': 0.03, 'stop_loss': 3.0, 'take_profit': 6.0},
        'SIDEWAYS_LOW': {'position_size': 0.015, 'stop_loss': 1.5, 'take_profit': 3.0},
        'SIDEWAYS_MEDIUM': {'position_size': 0.02, 'stop_loss': 2.0, 'take_profit': 4.0},
        'SIDEWAYS_HIGH': {'position_size': 0.025, 'stop_loss': 2.5, 'take_profit': 5.0}
    }
    
    # Risk Management
    STOP_LOSS_PERCENTAGE = 2.0  # 2% stop loss
    TAKE_PROFIT_PERCENTAGE = 4.0  # 4% take profit
    MAX_DAILY_TRADES = 15  # Increased for more opportunities
    MAX_DAILY_LOSS = 3.0  # Reduced for better risk control
    
    # Dynamic Position Sizing
    BASE_POSITION_SIZE = 0.02  # 2% of balance per trade
    MAX_POSITION_SIZE = 0.10  # 10% max position size
    VOLATILITY_ADJUSTMENT = True  # Adjust position size based on volatility
    KELLY_CRITERION = True  # Use Kelly Criterion for optimal sizing
    
    # Advanced Risk Controls
    CORRELATION_LIMIT = 0.7  # Maximum correlation between trades
    MAX_CONCURRENT_POSITIONS = 3  # Maximum open positions
    TRAILING_STOP = True  # Enable trailing stop-loss
    TRAILING_STOP_PERCENTAGE = 1.5  # 1.5% trailing stop
    
    # Monitoring Configuration
    UPDATE_INTERVAL = 5  # seconds
    DATA_RETRIEVAL_INTERVAL = 60  # seconds
    
    # Database Configuration
    DATABASE_PATH = 'tradex.db'
    LOG_FILE = 'tradex.log'
    
    # Paper Trading Mode
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
