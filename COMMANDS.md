# 🎮 TradeX Menu System - Quick Commands Reference

## 🚀 **Start Here - One Command to Rule Them All**

```bash
python3 tradex_menu.py
```

**That's it!** The menu system will guide you through everything.

---

## 📋 **Menu System Overview**

### **Main Menu Categories:**

1. **Setup & Installation** - Get everything ready
2. **Testing & Validation** - Make sure it works  
3. **Machine Learning Training** - Train the AI models
4. **Trading Operations** - Start trading (paper or live)
5. **Backtesting** - Test strategies with historical data
6. **Reporting & Analytics** - View performance and generate reports
7. **System Maintenance** - Keep everything running smoothly
8. **Help & Documentation** - Get help when you need it

---

## 🎯 **Quick Start Guide**

### **Step 1: Setup**
```bash
python3 tradex_menu.py
# Choose: Setup & Installation → Virtual Environment Setup
```

### **Step 2: Test**
```bash
python3 tradex_menu.py
# Choose: Testing & Validation → System Test
```

### **Step 3: Train**
```bash
python3 tradex_menu.py
# Choose: Machine Learning Training → Train Models
```

### **Step 4: Paper Trading**
```bash
python3 tradex_menu.py
# Choose: Trading Operations → Paper Trading
```

### **Step 5: Live Trading (When Ready)**
```bash
python3 tradex_menu.py
# Choose: Trading Operations → Live Trading
```

---

## 🔧 **Direct Commands (Advanced Users)**

### **Setup Commands**
```bash
# Virtual environment setup
python3 setup_venv.py

# Jetson setup (automated)
./setup_jetson.sh

# Fix dependencies
./fix_dependencies.sh

# Fix TensorFlow specifically
python3 fix_tensorflow.py

# Fix architecture issues (ELF header errors)
python3 fix_architecture.py
```

### **Testing Commands**
```bash
# Comprehensive system test
python3 test_system.py

# Basic functionality test
python3 basic_test.py
```

### **Training Commands**
```bash
# Train all ML models
python3 main.py --mode train

# Train models directly
python3 train_models.py
```

### **Trading Commands**
```bash
# Paper trading (safe)
python3 main.py --mode paper

# Live trading (real money)
python3 main.py --mode trade

# Start with monitoring
python3 start_tradex.py
```

### **Backtesting Commands**
```bash
# Quick backtest ($1000, last month)
python3 main.py --mode backtest

# Custom backtest
python3 main.py --mode backtest --start-date 2024-01-01 --end-date 2024-01-31 --initial-balance 1000
```

### **Reporting Commands**
```bash
# Generate PDF report (last 30 days)
python3 main.py --mode report

# Custom report
python3 main.py --mode report --days 60 --output my_report.pdf
```

---

## 🛠️ **Troubleshooting**

### **Common Issues & Solutions**

#### **"ModuleNotFoundError: No module named 'loguru'"**
```bash
python3 tradex_menu.py
# Choose: Setup & Installation → Fix Dependencies
```

#### **"TensorFlow import failed"**
```bash
python3 tradex_menu.py
# Choose: Setup & Installation → Fix TensorFlow
```

#### **"invalid ELF header" or "architecture mismatch"**
```bash
python3 tradex_menu.py
# Choose: Setup & Installation → Fix Architecture Issues
```

#### **"Virtual environment not found"**
```bash
python3 tradex_menu.py
# Choose: Setup & Installation → Virtual Environment Setup
```

#### **"API connection failed"**
```bash
python3 tradex_menu.py
# Choose: Testing & Validation → API Test
```

#### **"Permission denied"**
```bash
chmod +x *.sh *.py
```

---

## 📊 **Service Commands (Systemd)**

### **Install as Service**
```bash
sudo cp tradex.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tradex
sudo systemctl start tradex
```

### **Service Management**
```bash
# Check status
sudo systemctl status tradex

# Start service
sudo systemctl start tradex

# Stop service
sudo systemctl stop tradex

# Restart service
sudo systemctl restart tradex

# View logs
sudo journalctl -u tradex -f
```

---

## 🎮 **Menu System Features**

### **✅ What the Menu Does:**
- **Automatic virtual environment activation**
- **Command confirmation prompts**
- **Error handling and recovery**
- **System status checking**
- **Built-in help and documentation**
- **User-friendly interface**

### **✅ Safety Features:**
- **Multiple confirmations for live trading**
- **Clear warnings for dangerous operations**
- **Automatic dependency checking**
- **System health monitoring**

---

## 🎉 **Ready to Start?**

1. **Clone the repository**
2. **Run**: `python3 tradex_menu.py`
3. **Follow the menu prompts**

**That's it!** The menu system handles everything else.

---

**💡 Pro Tip**: Use the menu system for everything - it's designed to make TradeX easy and safe to use!
