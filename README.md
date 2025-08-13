# TradeX - Professional Trading Bot Platform

A complete, professional-grade cryptocurrency trading bot platform with real-time market data, custom Pine Script strategies, and comprehensive monitoring dashboard.

## 🚀 Features

- **Real-time Market Data**: Live BTC/ETH prices from Coinbase API
- **Custom Pine Script Editor**: Write and deploy your own trading strategies
- **Professional Dashboard**: Real-time portfolio metrics, trade history, and system monitoring
- **Paper Trading**: Safe simulation mode with realistic market conditions
- **Persistent Data**: All trades and strategies saved to SQLite database
- **System Health Monitoring**: Comprehensive health checks and logging
- **Responsive Design**: Modern, professional UI with dark theme

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **npm** (comes with Node.js)
- **Git** (for cloning the repository)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TradeX.git
cd TradeX
```

### 2. Install Dependencies
```bash
# Install backend dependencies
npm install

# Install frontend dependencies
cd client
npm install
cd ..
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```bash
# Trading Configuration
TRADING_MODE=paper
PORT=5000

# API Keys (for real trading - optional)
# ALPACA_API_KEY=your_alpaca_api_key  # Not needed for paper trading simulation
ALPACA_SECRET_KEY=your_alpaca_secret_key
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET=your_coinbase_secret

# Database Configuration
DATABASE_PATH=./data/tradex.db

# Logging Configuration
LOG_LEVEL=info
LOG_FILE_PATH=./logs/tradex.log
```

### 4. Create Required Directories
```bash
mkdir -p data logs
```

## 🚀 Running the Application

### 🚀 **Quick Start (Recommended)**
```bash
# Start everything with one command
./start.sh
```

This will:
- ✅ Start the backend server (port 5000)
- ✅ Start the frontend server (port 3000)
- ✅ Open the dashboard automatically in your browser
- ✅ Show live logs in the terminal

### 🛑 **Stop the Application**
```bash
# Stop everything with one command
./stop.sh
```

### 📋 **Manual Start (Alternative)**
1. **Start the Backend Server**:
```bash
npm start
```

2. **Start the Frontend** (in a new terminal):
```bash
cd client
npm start
```

3. **Access the Dashboard**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Production Mode

1. **Build the Frontend**:
```bash
cd client
npm run build
cd ..
```

2. **Start in Production Mode**:
```bash
NODE_ENV=production npm start
```

## 📊 Dashboard Features

### Trading Control
- **Start/Stop Trading**: Control the trading bot
- **Restart Session**: Clear all data and start fresh
- **Trading Mode**: Switch between paper and real trading

### Portfolio Metrics
- **Total P&L**: Real-time profit/loss calculation
- **Total Trades**: Number of executed trades
- **Portfolio Value**: Current portfolio worth

### Pine Script Editor
- **BTC Strategy**: Custom Pine Script for Bitcoin
- **ETH Strategy**: Custom Pine Script for Ethereum
- **Real-time Updates**: Strategies applied immediately

### Trade History
- **Detailed Trade Log**: Every trade with timestamps
- **P&L per Trade**: Individual trade performance
- **Real-time Updates**: Live trade feed

### System Monitoring
- **Health Status**: System component status
- **Performance Metrics**: CPU, memory, network usage
- **Trading Logs**: Real-time system logs

## 🔧 Configuration

### Trading Strategies
The platform supports custom Pine Script strategies for both BTC and ETH:

```pinescript
// Example: Moving Average Crossover
fastMA = sma(close, 10)
slowMA = sma(close, 20)

buySignal = fastMA > slowMA and fastMA[1] <= slowMA[1]
sellSignal = fastMA < slowMA and fastMA[1] >= slowMA[1]

if buySignal
    strategy.entry('Long', strategy.long)
if sellSignal
    strategy.close('Long')
```

### API Configuration
- **Paper Trading**: Uses Coinbase prices for simulation
- **Real Trading**: Requires valid API keys for Alpaca/Coinbase

## 📁 Project Structure

```
TradeX/
├── client/                 # React frontend
│   ├── public/            # Static files
│   ├── src/               # React components
│   └── package.json       # Frontend dependencies
├── server/                # Node.js backend
│   ├── modules/           # Core trading modules
│   ├── routes/            # API routes
│   └── index.js           # Server entry point
├── data/                  # Database files (auto-created)
├── logs/                  # Log files (auto-created)
├── package.json           # Backend dependencies
└── README.md             # This file
```

## 🔒 Security

- **Environment Variables**: Sensitive data stored in .env
- **API Rate Limiting**: Built-in protection against abuse
- **Input Validation**: All API inputs validated
- **Error Handling**: Comprehensive error management

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Kill existing processes
   pkill -f "node.*server"
   ```

2. **Database Issues**:
   ```bash
   # Remove and recreate database
   rm -rf data/
   mkdir data/
   ```

3. **Frontend Not Loading**:
   ```bash
   # Clear npm cache
   npm cache clean --force
   # Reinstall dependencies
   rm -rf node_modules/
   npm install
   ```

### Logs
Check the logs for detailed error information:
```bash
tail -f logs/tradex.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**Happy Trading! 🚀💰**
