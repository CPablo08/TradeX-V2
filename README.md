# TradeX V3 - Automated BTC Trading Platform

A sophisticated automated trading platform specifically designed for Bitcoin (BTC) trading, featuring advanced technical analysis, machine learning predictions, and comprehensive risk management.

## 🚀 Features

### Core Components
- **Data Retriever**: Real-time BTC price data from Binance API
- **ML Predictor**: Lightweight LSTM model for price prediction
- **Risk Module**: Dynamic stop-loss, take-profit, and position sizing
- **Logic Engine**: Weighted decision-making system
- **Executor**: Trade execution with paper trading support
- **Trade Logger**: Comprehensive analytics and performance tracking
- **Terminal Interface**: Beautiful interactive monitoring dashboard

### Advanced Features
- **Multi-timeframe Analysis**: 1m, 5m, 15m, 1h, 4h, 1d data integration
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Machine Learning**: LSTM-based price prediction with confidence scoring
- **Risk Management**: Dynamic position sizing, daily loss limits, trade frequency controls
- **Paper Trading**: Safe testing environment with simulated trading
- **Real-time Monitoring**: Live dashboard with market data and system status
- **Backtesting**: Historical performance analysis
- **Performance Analytics**: Comprehensive trade logging and metrics

## 📋 Requirements

- Python 3.8+
- Binance API credentials (optional for paper trading)
- Internet connection for market data

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TradeX
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   Create a `.env` file in the project root:
   ```env
   BINANCE_API_KEY=your_api_key_here
   BINANCE_SECRET_KEY=your_secret_key_here
   BINANCE_TESTNET=True
   ```

## 🚀 Usage

### Interactive Mode (Recommended for beginners)
```bash
python main.py
```
This launches the beautiful terminal interface with menu options for monitoring, testing, and analytics.

### Automated Trading Mode
```bash
python main.py auto
```
Runs the system in fully automated mode with continuous trading cycles.

### Backtesting Mode
```bash
python main.py backtest 2024-01-01 2024-01-31
```
Runs historical backtesting for the specified date range.

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Retriever│    │   ML Predictor  │    │   Risk Module   │
│                 │    │                 │    │                 │
│ • Binance API   │    │ • LSTM Model    │    │ • Stop Loss     │
│ • Technical     │    │ • Price Pred    │    │ • Take Profit   │
│   Indicators    │    │ • Confidence    │    │ • Position Size │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Logic Engine   │
                    │                 │
                    │ • Weighted      │
                    │   Decisions     │
                    │ • Signal        │
                    │   Generation    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │    Executor     │
                    │                 │
                    │ • Trade Exec    │
                    │ • Paper Trading │
                    │ • Order Mgmt    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Trade Logger   │
                    │                 │
                    │ • Performance   │
                    │ • Analytics     │
                    │ • Data Export   │
                    └─────────────────┘
```

## 🎯 Trading Strategy

The system uses a multi-factor decision-making approach:

1. **Technical Analysis (40%)**: RSI, MACD, Bollinger Bands, Moving Averages
2. **ML Prediction (30%)**: LSTM-based price prediction
3. **Trend Confirmation (20%)**: Multi-timeframe trend analysis
4. **Liquidity & Volatility (10%)**: Market condition assessment

### Decision Process
1. Fetch real-time market data
2. Calculate technical indicators
3. Generate ML prediction
4. Analyze market conditions
5. Apply risk management rules
6. Execute trade if conditions are met
7. Log all decisions and results

## ⚙️ Configuration

Key configuration options in `config.py`:

```python
# Trading Settings
SYMBOL = 'BTCUSDT'
PAPER_TRADING = True
UPDATE_INTERVAL = 60  # seconds

# Risk Management
STOP_LOSS_PERCENTAGE = 2.0
TAKE_PROFIT_PERCENTAGE = 4.0
MAX_DAILY_TRADES = 10
MAX_DAILY_LOSS = 5.0

# Logic Engine Weights
TECHNICAL_INDICATORS_WEIGHT = 0.4
ML_PREDICTION_WEIGHT = 0.3
TREND_CONFIRMATION_WEIGHT = 0.2
LIQUIDITY_VOLATILITY_WEIGHT = 0.1
```

## 📈 Performance Monitoring

The system provides comprehensive performance metrics:

- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Average Win/Loss**: Mean profit and loss per trade

## 🔒 Safety Features

- **Paper Trading Mode**: Test strategies without real money
- **Risk Limits**: Daily loss limits and trade frequency controls
- **Position Sizing**: Dynamic sizing based on account balance
- **Stop Loss**: Automatic loss protection
- **Error Handling**: Robust error handling and logging

## 📝 Logging

All system activities are logged to:
- Console output for real-time monitoring
- Daily log files in `logs/` directory
- SQLite database for trade history and analytics

## 🚨 Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss. Always test thoroughly in paper trading mode before using real funds. The authors are not responsible for any financial losses incurred through the use of this software.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the logs in the `logs/` directory
2. Review the configuration in `config.py`
3. Test in paper trading mode first
4. Open an issue on GitHub

---

**TradeX V3** - Advanced BTC Trading Platform
