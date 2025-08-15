# TradeX - Crypto Trading Automation Platform

A sophisticated automated trading platform for Bitcoin (BTC) and Ethereum (ETH) that combines traditional technical analysis with machine learning for pattern recognition and price prediction. **Designed for 24/7 crypto holdings trading with comprehensive safety protocols and automated monitoring.**

## Features

### 🤖 Machine Learning Engine
- **Ensemble Models**: Combines Random Forest, Gradient Boosting, and XGBoost for robust predictions
- **LSTM Neural Networks**: Deep learning for sequence prediction and pattern recognition
- **Feature Engineering**: 50+ technical indicators and chart patterns
- **Adaptive Learning**: Models retrain daily with new market data

### 📊 Technical Analysis
- **Chart Pattern Recognition**: Detects double tops/bottoms, head & shoulders, triangles, flags, cup & handle
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, Williams %R, CCI
- **Support/Resistance**: Dynamic level detection and distance analysis
- **Volume Analysis**: OBV, VWAP, volume ratios and surges

### 🛡️ Advanced Safety Protocols
- **Balance Protection**: Prevents selling below minimum crypto balances
- **Emergency Stop**: Automatic shutdown on consecutive errors
- **Position Sizing**: Dynamic sizing based on ML confidence and volatility
- **Stop-Loss/Take-Profit**: Automated risk management
- **Drawdown Protection**: Maximum 15% drawdown limit
- **Correlation Analysis**: Avoids over-exposure to correlated assets
- **Daily Trade Limits**: Prevents overtrading
- **Real-time Balance Monitoring**: Continuous account balance verification

### 🔄 24/7 Automation & Monitoring
- **System Health Monitoring**: Real-time CPU, memory, and disk usage tracking
- **Automatic Recovery**: Self-healing system with automatic restart capabilities
- **Network Connectivity**: Continuous network and API connectivity checks
- **State Persistence**: Automatic state saving and recovery across restarts
- **Graceful Shutdown**: Proper cleanup and position management on shutdown
- **Process Monitoring**: External monitor process for system reliability
- **Comprehensive Logging**: Detailed logs with automatic rotation
- **Live Status Dashboard**: Real-time system status updates every 2 seconds

### 🔄 Automated Trading
- **24/7 Operation**: Designed for Jetson Orin Nano deployment
- **Real-time Analysis**: Hourly market analysis and decision making
- **Coinbase Integration**: Direct API connection for execution
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Crypto Holdings Trading**: Works with your existing BTC/ETH holdings

### 📈 Backtesting Engine
- **Historical Data Testing**: Tests with real Coinbase historical data
- **Complete System Simulation**: Tests entire trading logic including ML models
- **Performance Analytics**: Comprehensive metrics and risk analysis
- **Visual Reports**: Charts and graphs for performance analysis
- **Risk Metrics**: Sharpe ratio, drawdown, volatility analysis

## Installation

### Prerequisites
- Python 3.8+
- Jetson Orin Nano (recommended) or any Linux system
- Coinbase Advanced Trade API credentials
- Existing BTC/ETH holdings in Coinbase account

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd TradeX
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env_example.txt .env
# Edit .env with your Coinbase API passphrase only
# API Key and Secret are already configured
```

4. **Get Coinbase API credentials**
- Go to https://pro.coinbase.com/profile/api
- Create a new API key with trading permissions
- Add only the passphrase to your `.env` file

## Usage

### 🚀 **Single Command Startup (Recommended)**
```bash
python start_tradex.py
```
This single command will:
- ✅ Check environment and dependencies
- ✅ Start the trading system automatically
- ✅ Start the external monitor
- ✅ Display live status dashboard (updates every 2 seconds)
- ✅ Handle graceful shutdown with Ctrl+C

### Training ML Models (First Time)
```bash
python main.py --mode train
```
This will:
- Collect historical data from Coinbase
- Calculate technical indicators and identify patterns
- Train ensemble and LSTM models
- Save models to `models/` directory

### 📈 **Backtesting (Test Your Strategy)**
```bash
# Test last 30 days (default)
python main.py --mode backtest

# Test specific date range
python main.py --mode backtest --start-date 2024-01-01 --end-date 2024-01-31

# Test with different initial balance
python main.py --mode backtest --initial-balance 5000

# Run backtest directly
python backtest_engine.py --start-date 2024-01-01 --end-date 2024-01-31
```

### 📝 **Paper Trading (Simulated Live Trading)**
```bash
# Start paper trading with real market data
python main.py --mode paper

# Paper trading uses real market data but simulates all trades
# Perfect for testing your strategy before going live
```

### Alternative Startup Methods

#### Manual Startup (Advanced Users)
```bash
# Terminal 1: Start trading system
python main.py --mode trade

# Terminal 2: Start monitor (optional)
python monitor.py
```

#### Systemd Service (Production)
```bash
# Install as system service
sudo systemctl enable tradex
sudo systemctl start tradex

# Monitor the service
sudo systemctl status tradex
tail -f tradex.log
```

### Dry Run (Testing)
```bash
python main.py --mode trade --dry-run
```

## Live Status Dashboard

When you run `python start_tradex.py`, you'll see a live dashboard that updates every 2 seconds:

```
================================================================================
🔄 TRADEX SYSTEM STATUS
================================================================================
⏰ Time: 2024-01-15 14:30:25
⏱️  Uptime: 0:02:15

✅ Trading System: RUNNING (PID: 12345)
   📊 Memory: 2.3% | CPU: 1.2%
✅ Monitor: RUNNING (PID: 12346)
   📊 Memory: 0.8% | CPU: 0.3%

💻 SYSTEM RESOURCES:
   🧠 Memory: 45.2%
   🔥 CPU: 12.8%
   💾 Disk: 23.1%

🌐 NETWORK STATUS:
   ✅ Network: CONNECTED
   ✅ Coinbase API: CONNECTED

📈 TRADING STATUS:
   🟡 Trading: RUNNING (Monitoring markets)

🔧 QUICK ACTIONS:
   Press Ctrl+C to stop TradeX
   Check logs: tail -f tradex.log
   Check state: cat system_state.json
================================================================================
```

## Backtesting Results

After running a backtest, you'll get comprehensive results:

```
================================================================================
📊 TRADEX BACKTEST RESULTS
================================================================================
📅 Period: 2024-01-01 to 2024-01-31
💰 Initial Balance: $1,000.00
💰 Final Balance: $1,085.00
📈 Total Return: $85.00 (8.50%)

📊 TRADING METRICS:
   🔄 Total Trades: 45
   ✅ Winning Trades: 28
   ❌ Losing Trades: 17
   🎯 Win Rate: 62.2%
   💵 Total P&L: $850.00
   📈 Average Win: $45.20
   📉 Average Loss: -$25.80
   ⚖️  Profit Factor: 2.15

📊 RISK METRICS:
   📊 Volatility: 0.25
   📈 Sharpe Ratio: 1.85
   📉 Max Drawdown: 3.20%

📁 REPORTS SAVED TO:
   📄 backtest_reports/performance_metrics.json
   📄 backtest_reports/trade_history.csv
   📄 backtest_reports/daily_balances.csv
   📊 backtest_reports/performance_plots.png
================================================================================
```

## Configuration

Edit `config.py` to customize trading parameters:

```python
# Trading Parameters - Modified for crypto holdings
TRADE_AMOUNT_USD = 100  # USD equivalent per trade
MAX_POSITION_SIZE = 0.1  # 10% of portfolio per position
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENTAGE = 0.04  # 4% take profit

# Safety Protocols
MAX_DAILY_TRADES = 10
MAX_DRAWDOWN = 0.15  # 15% maximum drawdown

# Balance Safety Limits
MIN_BTC_BALANCE = 0.001  # Minimum BTC to keep (prevent selling all)
MIN_ETH_BALANCE = 0.01   # Minimum ETH to keep (prevent selling all)
MIN_USD_BALANCE = 50     # Minimum USD to keep for fees

# 24/7 Automation Settings
HEARTBEAT_INTERVAL = 300  # 5 minutes - system health check interval
MAX_CONSECUTIVE_ERRORS = 5  # Emergency stop after this many errors
MAX_RECOVERY_ATTEMPTS = 10  # Maximum recovery attempts before exit
```

## Safety Features

### 🚨 Emergency Protocols
- **Automatic Shutdown**: Stops trading after 5 consecutive errors
- **Balance Verification**: Checks account balances before every trade
- **Minimum Balance Protection**: Never sells below minimum crypto amounts
- **Real-time Monitoring**: Continuous balance and error tracking
- **System Health Checks**: Monitors CPU, memory, and disk usage
- **Network Monitoring**: Continuous connectivity verification

### 💰 Balance Management
- **Smart Position Sizing**: Calculates safe trade amounts based on available balances
- **USD Reserve**: Maintains minimum USD balance for fees
- **Crypto Reserves**: Keeps minimum BTC/ETH amounts
- **Portfolio Limits**: Maximum 10% of portfolio per position

### 📊 Risk Controls
- **Daily Limits**: Maximum 10 trades per day
- **Stop Losses**: Automatic 2% stop loss on all positions
- **Take Profits**: 4% take profit targets
- **Drawdown Protection**: Automatic pause at 15% drawdown
- **Correlation Limits**: Avoids trading when BTC/ETH correlation > 70%

### 🔧 24/7 Reliability
- **State Persistence**: Saves system state every hour for recovery
- **Automatic Recovery**: Attempts to recover from errors automatically
- **Process Monitoring**: External monitor ensures system stays running
- **Graceful Shutdown**: Proper cleanup on system shutdown
- **Resource Monitoring**: Tracks system resources and warns of issues

## Machine Learning Strategy

### Pattern Recognition
The ML system learns to recognize:
- **Reversal Patterns**: Double tops/bottoms, head & shoulders
- **Continuation Patterns**: Triangles, flags, pennants
- **Candlestick Patterns**: Doji, hammer, shooting star
- **Volume Patterns**: Breakouts, accumulation/distribution

### Feature Engineering
- **Price Action**: Returns, volatility, support/resistance distances
- **Technical Indicators**: 20+ momentum, trend, and volatility indicators
- **Volume Analysis**: Volume ratios, OBV, VWAP
- **Pattern Features**: Binary indicators for each detected pattern
- **Time Series Features**: Lagged values and rolling statistics

### Model Architecture
- **Ensemble Model**: Combines predictions from multiple algorithms
- **LSTM Model**: Processes sequential data for temporal patterns
- **Confidence Scoring**: Probability-based decision making
- **Adaptive Thresholds**: Dynamic signal thresholds based on market conditions

## Deployment on Jetson Orin Nano

### System Requirements
- Jetson Orin Nano Developer Kit
- 8GB RAM (minimum)
- 32GB eMMC storage
- Ubuntu 20.04 or later

### Setup Commands
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv

# Create virtual environment
python3 -m venv tradex_env
source tradex_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Set up systemd service for auto-start
sudo cp tradex.service /etc/systemd/system/
sudo systemctl enable tradex
sudo systemctl start tradex
```

### Quick Start (Recommended)
```bash
# Just run this one command!
python start_tradex.py
```

### Monitoring Commands
```bash
# Check service status
sudo systemctl status tradex

# View trading logs
tail -f tradex.log

# View monitor logs
tail -f monitor.log

# Monitor system resources
htop
nvidia-smi

# Check system state
cat system_state.json
```

## File Structure

```
TradeX/
├── start_tradex.py        # 🚀 Single startup script (NEW!)
├── main.py                 # Main entry point
├── config.py              # Configuration settings
├── trading_engine.py      # Main trading logic with 24/7 protocols
├── data_collector.py      # Data collection and analysis
├── ml_engine.py           # Machine learning models
├── risk_manager.py        # Risk management
├── train_models.py        # Model training script
├── backtest_engine.py     # 📈 Backtesting engine (NEW!)
├── monitor.py             # External system monitor
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── tradex.service         # Systemd service file
├── models/                # Trained ML models
├── logs/                  # Log files
├── backtest_reports/      # 📊 Backtest results (NEW!)
├── system_state.json      # System state persistence
└── README.md             # This file
```

## Monitoring and Logs

The system provides comprehensive logging:
- **Trading Logs**: All trades, signals, and decisions
- **ML Logs**: Model predictions and confidence scores
- **Risk Logs**: Position management and risk metrics
- **Safety Logs**: Balance checks and emergency protocols
- **System Logs**: Health monitoring and recovery attempts
- **Monitor Logs**: External monitoring and restart events
- **Launcher Logs**: Startup and shutdown events
- **Backtest Logs**: Historical testing results
- **Error Logs**: API errors and system issues

Logs are automatically rotated daily and kept for 7 days.

## 24/7 Operation Features

### 🔄 Automatic Recovery
- **Self-healing**: Automatically recovers from network issues
- **Model Reloading**: Reloads ML models if they become corrupted
- **State Restoration**: Restores trading state after restarts
- **Error Recovery**: Attempts to recover from consecutive errors

### 📊 Health Monitoring
- **System Resources**: Monitors CPU, memory, and disk usage
- **Network Status**: Checks connectivity to Coinbase API
- **Process Health**: Verifies trading process is responsive
- **Performance Metrics**: Tracks system performance over time

### 🛡️ Reliability Features
- **Graceful Shutdown**: Proper cleanup on system shutdown
- **State Persistence**: Saves state every hour for recovery
- **External Monitoring**: Separate monitor process for reliability
- **Automatic Restart**: Restarts system if it becomes unresponsive

## Disclaimer

This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Use at your own risk. The authors are not responsible for any financial losses.

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. **Use the single startup command**: `python start_tradex.py`
2. **Test your strategy first**: `python main.py --mode backtest`
3. Check the logs in `tradex.log` and `monitor.log`
4. Review the configuration in `config.py`
5. Ensure your Coinbase API credentials are correct
6. Verify your internet connection and API access
7. Check that you have sufficient crypto balances
8. Monitor system resources with `htop` and `nvidia-smi`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
