# TradeX Jetson Orin Nano Setup Guide

## 🚀 Quick Start Commands

### 1. Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv tradex_env
source tradex_env/bin/activate

# Install base requirements
pip3 install -r requirements_jetson.txt

# Install TensorFlow for Jetson (NVIDIA optimized)
pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512 tensorflow==2.15.0+nv23.11
```

### 2. Setup Environment
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file with your Coinbase passphrase
nano .env
```

### 3. Test System
```bash
# Test basic functionality
python3 basic_test.py

# Test all imports
python3 minimal_test.py

# Test API connection
python3 test_api.py
```

## 📋 TradeX Commands

### Training Mode
```bash
# Train ML models with historical data
python3 main.py --mode train
```

### Backtesting Mode
```bash
# Run backtest with default settings ($1000 starting capital)
python3 main.py --mode backtest

# Run backtest with custom parameters
python3 main.py --mode backtest --start-date 2024-01-01 --end-date 2024-01-31 --initial-balance 1000
```

### Live Trading Mode
```bash
# Start 24/7 trading with live status dashboard
python3 start_tradex.py

# Or start trading directly
python3 main.py --mode trade
```

### Service Mode (24/7 Background)
```bash
# Install as system service
sudo cp tradex.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tradex
sudo systemctl start tradex

# Check service status
sudo systemctl status tradex

# View logs
sudo journalctl -u tradex -f
```

## 🔧 System Requirements

### Hardware
- **Jetson Orin Nano** (4GB or 8GB)
- **Storage**: 32GB+ (SSD recommended)
- **Network**: Stable internet connection
- **Power**: Reliable power supply

### Software
- **JetPack 5.1.2** or later
- **Python 3.8+**
- **CUDA 11.8** (included with JetPack)

## 🚨 Important Notes

### Performance Optimization
```bash
# Enable performance mode
sudo nvpmodel -m 0  # Max performance
sudo jetson_clocks  # Max clocks

# Check GPU usage
tegrastats
```

### Memory Management
```bash
# Monitor system resources
htop
free -h
df -h
```

### Network Configuration
```bash
# Test network connectivity
ping api.coinbase.com
curl -I https://api.coinbase.com
```

## 🛠️ Troubleshooting

### TensorFlow Issues
```bash
# Check TensorFlow installation
python3 -c "import tensorflow as tf; print(tf.__version__); print(tf.config.list_physical_devices('GPU'))"

# Reinstall if needed
pip3 uninstall tensorflow
pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512 tensorflow==2.15.0+nv23.11
```

### API Connection Issues
```bash
# Test API credentials
python3 test_api.py

# Check firewall
sudo ufw status
```

### Service Issues
```bash
# Restart service
sudo systemctl restart tradex

# Check logs
sudo journalctl -u tradex -n 50
```

## 📊 Monitoring

### Real-time Monitoring
```bash
# Start with live dashboard
python3 start_tradex.py

# Monitor system resources
watch -n 2 'tegrastats && echo "---" && free -h && echo "---" && df -h'
```

### Log Monitoring
```bash
# View real-time logs
tail -f logs/tradex.log

# Search for errors
grep -i error logs/tradex.log
```

## 🔒 Security

### Firewall Setup
```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw enable
```

### API Key Security
- Store API keys securely
- Use environment variables
- Regular key rotation
- Monitor API usage

## 📈 Performance Tips

1. **Use SSD storage** for faster data access
2. **Enable performance mode** with `nvpmodel -m 0`
3. **Monitor temperature** with `tegrastats`
4. **Optimize network** for low latency
5. **Regular system updates**

## 🆘 Support

If you encounter issues:
1. Check the logs: `tail -f logs/tradex.log`
2. Test individual components
3. Verify network connectivity
4. Check system resources
5. Review this setup guide

## 🎯 Success Indicators

✅ **System is ready when:**
- All tests pass (`basic_test.py`, `minimal_test.py`, `test_api.py`)
- TensorFlow GPU is detected
- API connection works
- Service starts without errors
- Live dashboard shows status updates
