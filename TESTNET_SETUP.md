# Binance Testnet Setup Guide

## 🎯 What is Binance Testnet?

Binance Testnet is a **free testing environment** that provides:
- ✅ Real market data (same as live trading)
- ✅ Simulated trading with fake money
- ✅ All trading pairs and features
- ✅ Perfect for testing TradeX safely
- ✅ No risk of losing real money

## 🚀 Quick Setup

### Step 1: Get Testnet API Credentials

1. **Visit Binance Testnet**: https://testnet.binance.vision/
2. **Log in with GitHub** (create account if needed)
3. **Create API Key**:
   - Click "Generate HMAC_SHA256 Key"
   - Save your API Key and Secret Key
   - **Important**: These are different from live trading keys!

### Step 2: Configure TradeX

1. **Copy environment template**:
   ```bash
   cp env_example.txt .env
   ```

2. **Edit .env file**:
   ```bash
   nano .env
   ```

3. **Add your testnet credentials**:
   ```env
   BINANCE_API_KEY=your_testnet_api_key_here
   BINANCE_SECRET_KEY=your_testnet_secret_key_here
   BINANCE_TESTNET=True
   PAPER_TRADING=True
   ```

### Step 3: Test Connection

Run the testnet connection test:
```bash
python3 test_binance_testnet.py
```

You should see:
```
✅ Testnet is properly configured!
✅ Basic connectivity: SUCCESS
✅ Exchange info: SUCCESS (Found BTCUSDT)
```

## 🔧 Testnet Features

### Available Trading Pairs
- **BTCUSDT** (Bitcoin)
- **ETHUSDT** (Ethereum)
- **BNBUSDT** (Binance Coin)
- **ADAUSDT** (Cardano)
- **DOTUSDT** (Polkadot)
- And many more...

### Simulated Balances
- **USDT**: 10,000 (fake money)
- **BTC**: 1.0 (fake Bitcoin)
- **ETH**: 10.0 (fake Ethereum)

### Real Market Data
- ✅ Live price feeds
- ✅ Historical data
- ✅ Order book data
- ✅ Trading volume
- ✅ Market depth

## 🎮 Testing Scenarios

### 1. Basic Trading Test
```bash
python3 main.py auto
```
This will run TradeX in automated mode with testnet data.

### 2. Backtesting
```bash
python3 main.py backtest 2024-01-01 2024-01-31
```
Test your strategy with historical testnet data.

### 3. Paper Trading
```bash
python3 main.py paper
```
Simulate live trading without real money.

## 🔒 Safety Features

### Testnet vs Live Trading
| Feature | Testnet | Live Trading |
|---------|---------|--------------|
| Money | Fake | Real |
| Risk | None | High |
| Data | Real | Real |
| Orders | Simulated | Real |
| Balances | Reset daily | Permanent |

### Automatic Protection
- ✅ **Testnet Mode**: Always uses testnet by default
- ✅ **Paper Trading**: Simulates all trades
- ✅ **No Real Money**: Impossible to lose real funds
- ✅ **Daily Reset**: Testnet balances reset daily

## 🚨 Important Notes

### Testnet Limitations
- **Daily Reset**: Balances reset every 24 hours
- **Limited History**: Some historical data may be limited
- **API Limits**: Same rate limits as live trading
- **No Withdrawals**: Cannot withdraw testnet funds

### Best Practices
1. **Always test first**: Use testnet before live trading
2. **Monitor performance**: Track your testnet results
3. **Validate strategy**: Ensure profitability before going live
4. **Check logs**: Review trading logs for issues

## 🔄 Switching to Live Trading

**⚠️ WARNING: Only switch to live trading after thorough testing!**

1. **Get Live API Credentials**:
   - Visit: https://www.binance.com/en/my/settings/api-management
   - Create new API key with trading permissions
   - **Never use testnet keys for live trading!**

2. **Update Configuration**:
   ```env
   BINANCE_API_KEY=your_live_api_key_here
   BINANCE_SECRET_KEY=your_live_secret_key_here
   BINANCE_TESTNET=False
   PAPER_TRADING=False  # ⚠️ Real trading!
   ```

3. **Start with Small Amounts**:
   - Begin with minimal position sizes
   - Monitor closely for the first few days
   - Gradually increase as confidence grows

## 🆘 Troubleshooting

### Common Issues

**"API authentication failed"**
- Check your API key and secret
- Ensure you're using testnet credentials for testnet
- Verify API key has trading permissions

**"Symbol not found"**
- Check symbol format (e.g., BTCUSDT not BTC/USDT)
- Verify symbol exists on testnet
- Use supported trading pairs

**"Connection timeout"**
- Check internet connection
- Verify testnet URL is accessible
- Try again in a few minutes

### Getting Help
1. **Check logs**: `tail -f tradex.log`
2. **Run tests**: `python3 test_binance_testnet.py`
3. **Review config**: Check `config.py` settings
4. **Testnet status**: Visit https://testnet.binance.vision/

## 🎯 Next Steps

1. **Set up testnet credentials**
2. **Run connection test**
3. **Start with paper trading**
4. **Test your strategy thoroughly**
5. **Monitor performance**
6. **Only then consider live trading**

---

**Remember**: Testnet is your safe playground. Use it extensively before risking real money! 🛡️
