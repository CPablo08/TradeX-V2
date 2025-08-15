# 🚀 TradeX - Crypto Trading Automation Platform

**24/7 Automated Trading for BTC and ETH with Machine Learning**

## 🎯 Quick Start

### 1. **Start the Menu System**
```bash
python3 tradex_menu.py
```

That's it! The menu system will guide you through everything.

## 📋 What TradeX Does

- 🤖 **24/7 Automated Trading** - Runs continuously on your Jetson Orin Nano
- 🧠 **Machine Learning** - Uses AI to predict market movements
- 📊 **Backtesting** - Test strategies with real historical data
- 📝 **Paper Trading** - Practice with real data, no real money
- 📈 **Live Trading** - Trade with real money when ready
- 📄 **PDF Reports** - Generate comprehensive performance reports
- 🛡️ **Safety Features** - Built-in risk management and safety protocols

## 🎮 Menu System Features

### **Main Menu Categories:**

1. **Setup & Installation** - Get everything ready
2. **Testing & Validation** - Make sure it works
3. **Machine Learning Training** - Train the AI models
4. **Trading Operations** - Start trading (paper or live)
5. **Backtesting** - Test strategies with historical data
6. **Reporting & Analytics** - View performance and generate reports
7. **System Maintenance** - Keep everything running smoothly
8. **Help & Documentation** - Get help when you need it

## 🚀 Getting Started

### **Step 1: Setup**
1. Run `python3 tradex_menu.py`
2. Choose "Setup & Installation"
3. Select "Virtual Environment Setup"
4. Follow the prompts

### **Step 2: Test**
1. Choose "Testing & Validation"
2. Select "System Test"
3. Verify everything works

### **Step 3: Train**
1. Choose "Machine Learning Training"
2. Select "Train Models"
3. Wait for training to complete

### **Step 4: Test Trading**
1. Choose "Trading Operations"
2. Select "Paper Trading"
3. Watch it trade with real data (no real money)

### **Step 5: Go Live (When Ready)**
1. Choose "Trading Operations"
2. Select "Live Trading"
3. Confirm twice to start real trading

## 💡 Key Features

### **Safety First**
- ✅ Paper trading mode for safe testing
- ✅ Multiple confirmation prompts for live trading
- ✅ Built-in risk management
- ✅ Automatic stop-loss and take-profit
- ✅ Balance protection to prevent over-selling

### **Smart Trading**
- ✅ Machine learning predictions
- ✅ Technical analysis indicators
- ✅ Chart pattern recognition
- ✅ 24/7 automated operation
- ✅ Real-time market data

### **Easy Monitoring**
- ✅ Terminal-based status updates
- ✅ PDF performance reports
- ✅ System health monitoring
- ✅ Automatic error recovery
- ✅ External watchdog for reliability

## 🔧 System Requirements

- **Hardware**: Jetson Orin Nano (recommended) or any Linux system
- **OS**: Ubuntu 20.04+ or Jetson Linux
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for market data

## 📁 Project Structure

```
TradeX-V2/
├── tradex_menu.py          # 🎮 Main menu system (START HERE)
├── main.py                 # Core trading engine
├── setup_venv.py          # Virtual environment setup
├── test_system.py         # System testing
├── config.py              # Configuration settings
├── trading_engine.py      # Trading logic
├── ml_engine.py           # Machine learning models
├── data_collector.py      # Market data collection
├── backtest_engine.py     # Backtesting framework
├── report_generator.py    # PDF report generation
├── requirements.txt       # Python dependencies
└── README_SIMPLE.md       # This file
```

## 🎯 Common Commands

### **Start Menu System**
```bash
python3 tradex_menu.py
```

### **Direct Commands (if needed)**
```bash
# Setup
python3 setup_venv.py

# Test
python3 test_system.py

# Train
python3 main.py --mode train

# Paper Trading
python3 main.py --mode paper

# Backtest
python3 main.py --mode backtest

# Generate Report
python3 main.py --mode report
```

## 🛠️ Troubleshooting

### **"ModuleNotFoundError"**
- Run the menu system: `python3 tradex_menu.py`
- Choose "Setup & Installation" → "Fix Dependencies"

### **"Virtual environment not found"**
- Run the menu system: `python3 tradex_menu.py`
- Choose "Setup & Installation" → "Virtual Environment Setup"

### **"API connection failed"**
- Check your Coinbase API credentials in `config.py`
- Verify internet connection
- Use the menu system to test API connection

## 📞 Support

### **Built-in Help**
- Use the menu system: `python3 tradex_menu.py`
- Choose "Help & Documentation" for guides and troubleshooting

### **Quick Reference**
- **Setup**: Menu → Setup & Installation
- **Test**: Menu → Testing & Validation
- **Train**: Menu → Machine Learning Training
- **Trade**: Menu → Trading Operations
- **Report**: Menu → Reporting & Analytics

## 🎉 Ready to Start?

1. **Clone the repository**
2. **Run**: `python3 tradex_menu.py`
3. **Follow the menu prompts**

That's it! The menu system will guide you through everything else.

---

**TradeX - Making Crypto Trading Simple and Automated** 🚀
