import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Binance Trading API Configuration
    # Paper Trading (Testnet) and Live Trading
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_binance_api_key_here')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'your_binance_secret_key_here')
    
    # Binance Paper Trading (Testnet) - True for testnet, False for live
    BINANCE_TESTNET = True
    
    # Binance API Base URLs
    BINANCE_TESTNET_URL = "https://testnet.binance.vision"     # Testnet (paper trading)
    BINANCE_LIVE_URL = "https://api.binance.com"               # Live trading
    BINANCE_WS_TESTNET = "wss://testnet.binance.vision/ws"     # WebSocket testnet
    BINANCE_WS_LIVE = "wss://stream.binance.com:9443/ws"       # WebSocket live
    
    # Get the appropriate base URL based on testnet setting
    BINANCE_BASE_URL = BINANCE_TESTNET_URL if BINANCE_TESTNET else BINANCE_LIVE_URL
    BINANCE_WS_URL = BINANCE_WS_TESTNET if BINANCE_TESTNET else BINANCE_WS_LIVE
    
    # Trading Parameters - Modified for crypto holdings
    TRADE_AMOUNT_USD = 100  # USD equivalent per trade
    MAX_POSITION_SIZE = 0.1  # 10% of portfolio per position
    STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
    TAKE_PROFIT_PERCENTAGE = 0.04  # 4% take profit
    
    # Safety Protocols
    MAX_DAILY_TRADES = 10
    MAX_DRAWDOWN = 0.15  # 15% maximum drawdown
    CORRELATION_THRESHOLD = 0.7  # Don't trade if BTC/ETH correlation > 0.7
    
    # Balance Safety Limits
    MIN_BTC_BALANCE = 0.001  # Minimum BTC to keep (prevent selling all)
    MIN_ETH_BALANCE = 0.01   # Minimum ETH to keep (prevent selling all)
    MIN_USD_BALANCE = 50     # Minimum USD to keep for fees
    
    # 24/7 Automation Settings
    HEARTBEAT_INTERVAL = 300  # 5 minutes - system health check interval
    MAX_CONSECUTIVE_ERRORS = 5  # Emergency stop after this many errors
    MAX_RECOVERY_ATTEMPTS = 10  # Maximum recovery attempts before exit
    SYSTEM_STATUS_INTERVAL = 6  # Hours between system status reports
    STATE_SAVE_INTERVAL = 60  # Minutes between state saves
    
    # System Health Thresholds
    MAX_MEMORY_USAGE = 90  # Percentage - warning if exceeded
    MAX_CPU_USAGE = 80     # Percentage - warning if exceeded
    MAX_DISK_USAGE = 90    # Percentage - warning if exceeded
    
    # Network and API Settings
    NETWORK_TIMEOUT = 10   # Seconds for network connectivity checks
    API_TIMEOUT = 30       # Seconds for API calls
    
    # Technical Indicators
    RSI_PERIOD = 14
    SMA_PERIOD = 50
    EMA_PERIOD = 20
    BB_PERIOD = 20
    BB_STD_DEV = 2
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # ML Model Parameters
    FEATURE_LOOKBACK = 100  # Number of historical candles for features
    PREDICTION_HORIZON = 24  # Hours ahead to predict
    MODEL_RETRAIN_INTERVAL = 24  # Hours between model retraining
    MIN_SAMPLES_FOR_TRAINING = 1000
    
    # Data Collection
    DATA_GRANULARITY = 3600  # 1 hour candles
    DATA_LOOKBACK_DAYS = 30  # Days of historical data to fetch
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "tradex.log"
    LOG_ROTATION = "1 day"  # Rotate logs daily
    LOG_RETENTION = "7 days"  # Keep logs for 7 days
    
    # Supported Assets (Binance crypto pairs)
    # Crypto trading pairs - Binance format
    SUPPORTED_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT']  # Crypto pairs
    # Popular crypto pairs for trading
    
    # ML Model Paths
    MODEL_DIR = "models/"
    FEATURE_SCALER_PATH = "models/feature_scaler.pkl"
    ENSEMBLE_MODEL_PATH = "models/ensemble_model.pkl"
    LSTM_MODEL_PATH = "models/lstm_model.h5"
    
    # System State Files
    SYSTEM_STATE_FILE = "system_state.json"
    TRAINING_SUMMARY_FILE = "training_summary.json"
