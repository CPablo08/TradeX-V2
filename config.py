import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Coinbase Advanced Trade API Configuration
    # Load from official file if available, otherwise use fallback
    def _load_coinbase_credentials():
        try:
            import json
            # Try new key file first
            with open('cdp_api_key (2).json', 'r') as f:
                data = json.load(f)
            return data['name'], data['privateKey']
        except:
            try:
                # Fallback to old key file
                with open('cdp_api_key (3).json', 'r') as f:
                    data = json.load(f)
                return data['name'], data['privateKey']
            except:
                # Final fallback to hardcoded values
                return ("organizations/b2689c0a-e1e7-4be2-bfb8-2bfae3fc4457/apiKeys/48ff83f4-5aa9-41fe-ac80-9f4209921b4e",
                        """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIA/W9rUU3BJsHpgolBqTIcvgq9qLUB/uBk2HtB7prgt+oAoGCCqGSM49
AwEHoUQDQgAEGj95OfomV/p5Dl+zaeoBoQb3tB6BrHp1riQSjHQeF51NI+j84QRX
XXuVZWAJNGQbYDP4Hl8Y4AXxeqPEcuhSyA==
-----END EC PRIVATE KEY-----""")
    
    CB_API_KEY_NAME, CB_PRIVATE_KEY = _load_coinbase_credentials()
    
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
    
    # Supported Assets
    SUPPORTED_PAIRS = ['BTC-USD', 'ETH-USD']
    
    # ML Model Paths
    MODEL_DIR = "models/"
    FEATURE_SCALER_PATH = "models/feature_scaler.pkl"
    ENSEMBLE_MODEL_PATH = "models/ensemble_model.pkl"
    LSTM_MODEL_PATH = "models/lstm_model.h5"
    
    # System State Files
    SYSTEM_STATE_FILE = "system_state.json"
    TRAINING_SUMMARY_FILE = "training_summary.json"
