# TradeX Quick Commands Reference

## 🚀 Setup Commands

### Automated Setup (Recommended)
```bash
# Run the complete setup script
./setup_jetson.sh
```

### Manual Setup
```bash
# Install dependencies
pip3 install -r requirements_jetson.txt

# Install TensorFlow for Jetson
pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512 tensorflow==2.15.0+nv23.11

# Setup environment
cp env_example.txt .env
nano .env  # Add your Coinbase passphrase
```

## 🧪 Test Commands

```bash
# Comprehensive system test (recommended)
python3 test_system.py

# Basic functionality test
python3 basic_test.py

# Full system test
python3 minimal_test.py

# API connection test
python3 test_api.py
```

## 🤖 Training Commands

```bash
# Train ML models
python3 main.py --mode train
```

## 📊 Backtesting Commands

```bash
# Quick backtest ($1000 starting capital)
python3 main.py --mode backtest

# Custom backtest
python3 main.py --mode backtest --start-date 2024-01-01 --end-date 2024-01-31 --initial-balance 1000
```

## 💰 Live Trading Commands

```bash
# Start with live dashboard (recommended)
python3 start_tradex.py

# Real trading (live with real money)
python3 main.py --mode trade

# Paper trading (simulated with real data)
python3 main.py --mode paper

# Quick paper trading (alternative)
python3 main.py --mode trade --paper
```

## 🔧 Service Commands

```bash
# Install as system service
sudo cp tradex.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tradex
sudo systemctl start tradex

# Service management
sudo systemctl status tradex
sudo systemctl restart tradex
sudo systemctl stop tradex

# View service logs
sudo journalctl -u tradex -f
```

## 📈 Monitoring Commands

```bash
# System resources
tegrastats
htop
free -h

# Application logs
tail -f logs/tradex.log
grep -i error logs/tradex.log

# Network test
ping api.coinbase.com
curl -I https://api.coinbase.com
```

## 🛠️ Troubleshooting Commands

```bash
# Check TensorFlow GPU
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Check disk space
df -h

# Check memory
free -h
```

## 🎯 Typical Workflow

1. **Setup**: `./setup_jetson.sh`
2. **Test**: `python3 test_api.py`
3. **Train**: `python3 main.py --mode train`
4. **Backtest**: `python3 main.py --mode backtest`
5. **Paper**: `python3 main.py --mode paper`
6. **Live**: `python3 start_tradex.py`

## 🚨 Emergency Commands

```bash
# Stop all trading
sudo systemctl stop tradex

# Kill all Python processes
pkill -f python3

# Emergency shutdown
sudo shutdown -h now
```
