import os
import time
import pandas as pd
import numpy as np
import requests
from loguru import logger
import schedule
from datetime import datetime, timedelta
from config import Config
from data_collector import DataCollector
from ml_engine import MLEngine
from risk_manager import RiskManager
import psutil
import signal
import sys

class TradingEngine:
    def __init__(self, paper_trading=False):
        # Paper trading mode
        self.paper_trading = paper_trading
        if self.paper_trading:
            logger.info("🔄 PAPER TRADING MODE ENABLED - No real trades will be placed")
        
        # Initialize Coinbase client
        self.api_key = Config.CB_API_KEY
        self.api_secret = Config.CB_API_SECRET
        self.passphrase = Config.CB_API_PASSPHRASE
        self.base_url = "https://api.coinbase.com/api/v3/brokerage"
        self.api_secret = Config.CB_API_SECRET
        self.passphrase = Config.CB_API_PASSPHRASE
        self.base_url = "https://api.coinbase.com/api/v3/brokerage"
        
        # Initialize components
        self.data_collector = DataCollector()
        self.ml_engine = MLEngine()
        self.risk_manager = RiskManager()
        
        # Trading state
        self.active_positions = {}
        self.daily_trades = 0
        self.last_trade_time = None
        self.portfolio_value = 0
        self.account_balances = {}
        
        # Safety state
        self.emergency_stop = False
        self.last_balance_check = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # 24/7 Automation state
        self.start_time = datetime.now()
        self.last_heartbeat = datetime.now()
        self.heartbeat_interval = 300  # 5 minutes
        self.system_health = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'disk_usage': 0,
            'network_status': True,
            'api_status': True,
            'last_successful_trade': None,
            'uptime_hours': 0
        }
        self.recovery_attempts = 0
        self.max_recovery_attempts = 10
        
        # Load ML models
        self.ml_engine.load_models()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("Trading Engine initialized with 24/7 automation protocols")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.graceful_shutdown()
        sys.exit(0)
    
    def graceful_shutdown(self):
        """Perform graceful shutdown procedures"""
        try:
            logger.info("Starting graceful shutdown...")
            
            # Close any open positions if needed
            self.close_all_positions()
            
            # Save current state
            self.save_system_state()
            
            # Log final statistics
            uptime = datetime.now() - self.start_time
            logger.info(f"System shutdown complete. Total uptime: {uptime}")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
    
    def close_all_positions(self):
        """Close all open positions"""
        try:
            for symbol in list(self.active_positions.keys()):
                logger.info(f"Closing position for {symbol}")
                # This would implement position closing logic
                # For now, just remove from tracking
                del self.active_positions[symbol]
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
    
    def save_system_state(self):
        """Save current system state for recovery"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'active_positions': self.active_positions,
                'daily_trades': self.daily_trades,
                'portfolio_value': self.portfolio_value,
                'account_balances': self.account_balances,
                'system_health': self.system_health
            }
            
            import json
            with open('system_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info("System state saved")
        except Exception as e:
            logger.error(f"Error saving system state: {e}")
    
    def load_system_state(self):
        """Load previous system state for recovery"""
        try:
            import json
            if os.path.exists('system_state.json'):
                with open('system_state.json', 'r') as f:
                    state = json.load(f)
                
                # Restore state
                self.active_positions = state.get('active_positions', {})
                self.daily_trades = state.get('daily_trades', 0)
                self.portfolio_value = state.get('portfolio_value', 0)
                self.account_balances = state.get('account_balances', {})
                
                logger.info("System state restored from previous session")
                return True
        except Exception as e:
            logger.error(f"Error loading system state: {e}")
        return False
    
    def check_system_health(self):
        """Monitor system health metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_health['memory_usage'] = memory.percent
            
            # CPU usage
            self.system_health['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_health['disk_usage'] = disk.percent
            
            # Uptime
            uptime = datetime.now() - self.start_time
            self.system_health['uptime_hours'] = uptime.total_seconds() / 3600
            
            # Check for critical issues
            if self.system_health['memory_usage'] > 90:
                logger.warning(f"High memory usage: {self.system_health['memory_usage']}%")
            
            if self.system_health['cpu_usage'] > 80:
                logger.warning(f"High CPU usage: {self.system_health['cpu_usage']}%")
            
            if self.system_health['disk_usage'] > 90:
                logger.warning(f"High disk usage: {self.system_health['disk_usage']}%")
            
            self.last_heartbeat = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return False
    
    def check_network_connectivity(self):
        """Check network connectivity"""
        try:
            import requests
            response = requests.get('https://api.coinbase.com', timeout=10)
            self.system_health['network_status'] = response.status_code == 200
            return self.system_health['network_status']
        except Exception as e:
            logger.error(f"Network connectivity check failed: {e}")
            self.system_health['network_status'] = False
            return False
    
    def check_api_connectivity(self):
        """Check Coinbase API connectivity"""
        try:
            # Simple API call to test connectivity
            accounts = self.client.get_accounts()
            self.system_health['api_status'] = True
            return True
        except Exception as e:
            logger.error(f"API connectivity check failed: {e}")
            self.system_health['api_status'] = False
            return False
    
    def attempt_recovery(self):
        """Attempt system recovery"""
        try:
            logger.info(f"Attempting system recovery (attempt {self.recovery_attempts + 1}/{self.max_recovery_attempts})")
            
            # Check network
            if not self.check_network_connectivity():
                logger.warning("Network connectivity issues detected")
                time.sleep(60)  # Wait 1 minute
                return False
            
            # Check API
            if not self.check_api_connectivity():
                logger.warning("API connectivity issues detected")
                time.sleep(60)  # Wait 1 minute
                return False
            
            # Reload ML models if needed
            if not self.ml_engine.is_trained:
                logger.info("Reloading ML models...")
                self.ml_engine.load_models()
            
            # Reset error counters on successful recovery
            self.consecutive_errors = 0
            self.emergency_stop = False
            self.recovery_attempts = 0
            
            logger.info("System recovery successful")
            return True
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            self.recovery_attempts += 1
            return False
    
    def check_account_balances(self):
        """Check and update account balances with safety limits"""
        try:
            accounts = self.client.get_accounts()
            self.account_balances = {}
            
            for account in accounts:
                currency = account['currency']
                available_balance = float(account['available_balance']['value'])
                total_balance = float(account['total_balance']['value'])
                
                self.account_balances[currency] = {
                    'available': available_balance,
                    'total': total_balance,
                    'currency': currency
                }
                
                logger.info(f"{currency} Balance: Available={available_balance:.6f}, Total={total_balance:.6f}")
            
            self.last_balance_check = datetime.now()
            self.consecutive_errors = 0  # Reset error counter on successful balance check
            
            return True
            
        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"Error checking account balances: {e}")
            
            if self.consecutive_errors >= self.max_consecutive_errors:
                logger.critical(f"Too many consecutive errors ({self.consecutive_errors}). Emergency stop activated.")
                self.emergency_stop = True
            
            return False
    
    def get_safe_trade_amount(self, symbol, side, current_price):
        """Calculate safe trade amount considering balance limits"""
        try:
            if side == 'buy':
                # Buying with USD - check USD balance
                usd_balance = self.account_balances.get('USD', {}).get('available', 0)
                usdc_balance = self.account_balances.get('USDC', {}).get('available', 0)
                total_usd = usd_balance + usdc_balance
                
                # Calculate trade amount in USD
                trade_amount_usd = Config.TRADE_AMOUNT_USD
                
                # Check if we have enough USD
                if total_usd < trade_amount_usd + Config.MIN_USD_BALANCE:
                    available_usd = max(0, total_usd - Config.MIN_USD_BALANCE)
                    if available_usd < 10:  # Minimum $10 trade
                        logger.warning(f"Insufficient USD for {symbol} buy. Available: ${available_usd:.2f}")
                        return 0
                    trade_amount_usd = available_usd
                
                return trade_amount_usd
                
            elif side == 'sell':
                # Selling crypto - check crypto balance
                if symbol == 'BTC-USD':
                    crypto_balance = self.account_balances.get('BTC', {}).get('available', 0)
                    min_balance = Config.MIN_BTC_BALANCE
                elif symbol == 'ETH-USD':
                    crypto_balance = self.account_balances.get('ETH', {}).get('available', 0)
                    min_balance = Config.MIN_ETH_BALANCE
                else:
                    logger.error(f"Unknown symbol for selling: {symbol}")
                    return 0
                
                # Calculate how much we can sell
                sellable_amount = crypto_balance - min_balance
                
                if sellable_amount <= 0:
                    logger.warning(f"Insufficient {symbol.split('-')[0]} for selling. Balance: {crypto_balance:.6f}")
                    return 0
                
                # Convert to USD equivalent
                trade_amount_usd = sellable_amount * current_price
                
                # Limit to maximum trade amount
                if trade_amount_usd > Config.TRADE_AMOUNT_USD:
                    trade_amount_usd = Config.TRADE_AMOUNT_USD
                
                return trade_amount_usd
            
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating safe trade amount: {e}")
            return 0
    
    def get_portfolio_value(self):
        """Get current portfolio value"""
        try:
            if not self.account_balances:
                self.check_account_balances()
            
            total_value = 0
            
            # Add USD/USDC
            usd_value = self.account_balances.get('USD', {}).get('available', 0)
            usdc_value = self.account_balances.get('USDC', {}).get('available', 0)
            total_value += usd_value + usdc_value
            
            # Add crypto values
            for symbol in ['BTC-USD', 'ETH-USD']:
                crypto = symbol.split('-')[0]
                crypto_balance = self.account_balances.get(crypto, {}).get('available', 0)
                
                if crypto_balance > 0:
                    try:
                        ticker = self.client.get_product_ticker(symbol)
                        price = float(ticker['price'])
                        total_value += crypto_balance * price
                    except Exception as e:
                        logger.error(f"Error getting price for {symbol}: {e}")
            
            self.portfolio_value = total_value
            return total_value
            
        except Exception as e:
            logger.error(f"Error getting portfolio value: {e}")
            return 0
    
    def calculate_position_size(self, symbol, confidence_score):
        """Calculate position size based on ML confidence and risk management"""
        try:
            # Get current price
            ticker = self.client.get_product_ticker(symbol)
            current_price = float(ticker['price'])
            
            # Base position size in USD
            base_size_usd = Config.TRADE_AMOUNT_USD
            
            # Adjust based on ML confidence
            if confidence_score > 0.8:
                size_multiplier = 1.5
            elif confidence_score > 0.6:
                size_multiplier = 1.0
            else:
                size_multiplier = 0.5
            
            # Adjust based on portfolio value
            portfolio_multiplier = min(self.portfolio_value / 10000, 2.0)  # Cap at 2x
            
            # Adjust based on volatility
            current_data, _ = self.data_collector.get_market_data(symbol)
            if current_data is not None:
                volatility = current_data['atr'].iloc[-1] / current_data['close'].iloc[-1]
                volatility_multiplier = max(0.5, 1 - volatility * 10)  # Reduce size for high volatility
            else:
                volatility_multiplier = 1.0
            
            final_size_usd = base_size_usd * size_multiplier * portfolio_multiplier * volatility_multiplier
            
            # Ensure it doesn't exceed maximum position size
            max_position = self.portfolio_value * Config.MAX_POSITION_SIZE
            final_size_usd = min(final_size_usd, max_position)
            
            return final_size_usd
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return Config.TRADE_AMOUNT_USD
    
    def analyze_market_conditions(self, symbol):
        """Analyze current market conditions using technical indicators and ML"""
        try:
            # Get market data
            df, patterns = self.data_collector.get_market_data(symbol)
            if df is None:
                return None
            
            # Prepare features for ML
            features_df = self.ml_engine.prepare_features(df, patterns)
            if features_df is None:
                return None
            
            # Get ML predictions
            ml_predictions = self.ml_engine.predict(features_df)
            
            # Technical analysis signals
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Trend analysis
            trend_bullish = (current['close'] > current['sma_20'] > current['sma_50'] and 
                           current['sma_20'] > prev['sma_20'])
            trend_bearish = (current['close'] < current['sma_20'] < current['sma_50'] and 
                           current['sma_20'] < prev['sma_20'])
            
            # Momentum analysis
            rsi_oversold = current['rsi'] < 30
            rsi_overbought = current['rsi'] > 70
            rsi_bullish_divergence = (current['rsi'] > prev['rsi'] and 
                                    current['close'] < prev['close'])
            rsi_bearish_divergence = (current['rsi'] < prev['rsi'] and 
                                    current['close'] > prev['close'])
            
            # Bollinger Bands analysis
            bb_squeeze = current['bb_width'] < df['bb_width'].rolling(20).mean().iloc[-1] * 0.8
            bb_breakout_up = current['close'] > current['bb_upper']
            bb_breakout_down = current['close'] < current['bb_lower']
            bb_bounce_up = (current['close'] > current['bb_lower'] and 
                          prev['close'] <= prev['bb_lower'])
            bb_bounce_down = (current['close'] < current['bb_upper'] and 
                            prev['close'] >= prev['bb_upper'])
            
            # Volume analysis
            volume_surge = current['volume_ratio'] > 1.5
            volume_decline = current['volume_ratio'] < 0.5
            
            # Support/Resistance analysis
            near_support = current['distance_to_support'] < 0.02
            near_resistance = current['distance_to_resistance'] < 0.02
            
            # Pattern analysis
            bullish_patterns = sum([
                patterns.get('double_bottom', False),
                patterns.get('inverse_head_shoulders', False),
                patterns.get('ascending_triangle', False),
                patterns.get('bull_flag', False),
                patterns.get('cup_handle', False)
            ])
            
            bearish_patterns = sum([
                patterns.get('double_top', False),
                patterns.get('head_shoulders', False),
                patterns.get('descending_triangle', False),
                patterns.get('bear_flag', False)
            ])
            
            # Combine signals
            bullish_signals = 0
            bearish_signals = 0
            
            # Technical signals
            if trend_bullish: bullish_signals += 2
            if trend_bearish: bearish_signals += 2
            if rsi_oversold: bullish_signals += 1
            if rsi_overbought: bearish_signals += 1
            if rsi_bullish_divergence: bullish_signals += 2
            if rsi_bearish_divergence: bearish_signals += 2
            if bb_bounce_up: bullish_signals += 1
            if bb_bounce_down: bearish_signals += 1
            if bb_breakout_up: bullish_signals += 2
            if bb_breakout_down: bearish_signals += 2
            if volume_surge and trend_bullish: bullish_signals += 1
            if volume_surge and trend_bearish: bearish_signals += 1
            if near_support: bullish_signals += 1
            if near_resistance: bearish_signals += 1
            
            # Pattern signals
            bullish_signals += bullish_patterns * 2
            bearish_signals += bearish_patterns * 2
            
            # ML signals
            if ml_predictions:
                if ml_predictions.get('combined_signal') == 1:
                    bullish_signals += 3
                elif ml_predictions.get('combined_signal') == -1:
                    bearish_signals += 3
                
                confidence = ml_predictions.get('combined_probability', 0.5)
                if confidence > 0.7:
                    if ml_predictions.get('combined_signal') == 1:
                        bullish_signals += 2
                    elif ml_predictions.get('combined_signal') == -1:
                        bearish_signals += 2
            
            # Market volatility
            volatility = current['atr'] / current['close']
            high_volatility = volatility > df['atr'].rolling(20).mean().iloc[-1] / df['close'].rolling(20).mean().iloc[-1] * 1.5
            
            return {
                'symbol': symbol,
                'current_price': current['close'],
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals,
                'signal_strength': abs(bullish_signals - bearish_signals),
                'trend': 'bullish' if bullish_signals > bearish_signals else 'bearish' if bearish_signals > bullish_signals else 'neutral',
                'ml_predictions': ml_predictions,
                'patterns': patterns,
                'volatility': volatility,
                'high_volatility': high_volatility,
                'volume_surge': volume_surge,
                'bb_squeeze': bb_squeeze,
                'rsi': current['rsi'],
                'sma_20': current['sma_20'],
                'sma_50': current['sma_50']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions for {symbol}: {e}")
            return None
    
    def should_trade(self, analysis):
        """Determine if we should trade based on analysis and risk management"""
        if not analysis:
            return False, None
        
        # Check emergency stop
        if self.emergency_stop:
            logger.warning("Trading blocked due to emergency stop")
            return False, None
        
        # Check daily trade limit
        if self.daily_trades >= Config.MAX_DAILY_TRADES:
            logger.info(f"Daily trade limit reached ({Config.MAX_DAILY_TRADES})")
            return False, None
        
        # Check signal strength
        min_signal_strength = 5
        if analysis['signal_strength'] < min_signal_strength:
            return False, None
        
        # Check ML confidence
        if analysis['ml_predictions']:
            confidence = analysis['ml_predictions'].get('combined_probability', 0.5)
            if confidence < 0.6:
                return False, None
        
        # Check volatility
        if analysis['high_volatility']:
            logger.info(f"High volatility detected for {analysis['symbol']}, reducing position size")
        
        # Determine trade direction
        if analysis['bullish_signals'] > analysis['bearish_signals']:
            return True, 'buy'
        elif analysis['bearish_signals'] > analysis['bullish_signals']:
            return True, 'sell'
        
        return False, None
    
    def place_order(self, symbol, side, amount_usd):
        """Place order with enhanced safety checks"""
        try:
            # Get current price
            ticker = self.client.get_product_ticker(symbol)
            current_price = float(ticker['price'])
            
            # Calculate safe trade amount
            safe_amount = self.get_safe_trade_amount(symbol, side, current_price)
            
            if safe_amount <= 0:
                logger.warning(f"Cannot place {side} order for {symbol} - insufficient balance")
                return None
            
            # Use the smaller of calculated amount and safe amount
            final_amount = min(amount_usd, safe_amount)
            
            # Paper trading mode - simulate order placement
            if self.paper_trading:
                logger.info(f"📝 PAPER TRADE: {symbol} {side} ${final_amount:.2f} @ ${current_price:.2f}")
                
                # Simulate order response
                order = {
                    'id': f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'product_id': symbol,
                    'side': side,
                    'funds': final_amount if side == 'buy' else None,
                    'size': final_amount / current_price if side == 'sell' else None,
                    'status': 'filled',
                    'created_time': datetime.now().isoformat()
                }
                
                # Update trading state
                self.daily_trades += 1
                self.last_trade_time = datetime.now()
                self.system_health['last_successful_trade'] = datetime.now().isoformat()
                
                # Update position tracking for paper trading
                if side == 'buy':
                    self.active_positions[symbol] = {
                        'entry_price': current_price,
                        'entry_time': datetime.now(),
                        'position_size': final_amount,
                        'paper_trade': True
                    }
                elif side == 'sell' and symbol in self.active_positions:
                    # Close paper position
                    entry_price = self.active_positions[symbol]['entry_price']
                    pnl = ((current_price - entry_price) / entry_price) * 100
                    logger.info(f"📝 PAPER TRADE CLOSED: {symbol} P&L: {pnl:.2f}%")
                    del self.active_positions[symbol]
                
                return order
            
            # Real trading mode
            # Check if we have sufficient funds
            if side == 'buy':
                # Check USD balance
                usd_balance = self.account_balances.get('USD', {}).get('available', 0)
                usdc_balance = self.account_balances.get('USDC', {}).get('available', 0)
                total_usd = usd_balance + usdc_balance
                
                if total_usd < final_amount:
                    logger.warning(f"Insufficient USD for {symbol} {side} order. Need: ${final_amount:.2f}, Have: ${total_usd:.2f}")
                    return None
                
                # Place the order
                order = self.client.place_market_order(
                    product_id=symbol,
                    side=side,
                    funds=final_amount
                )
                
            elif side == 'sell':
                # Check crypto balance
                crypto = symbol.split('-')[0]
                crypto_balance = self.account_balances.get(crypto, {}).get('available', 0)
                
                # Calculate crypto amount to sell
                crypto_amount = final_amount / current_price
                
                if crypto_balance < crypto_amount:
                    logger.warning(f"Insufficient {crypto} for {symbol} {side} order. Need: {crypto_amount:.6f}, Have: {crypto_balance:.6f}")
                    return None
                
                # Place the order
                order = self.client.place_market_order(
                    product_id=symbol,
                    side=side,
                    size=crypto_amount
                )
            
            logger.info(f"Order placed: {symbol} {side} ${final_amount:.2f}")
            
            # Update trading state
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            self.system_health['last_successful_trade'] = datetime.now().isoformat()
            
            # Update position tracking
            if order and side == 'buy':
                self.active_positions[symbol] = {
                    'entry_price': current_price,
                    'entry_time': datetime.now(),
                    'position_size': final_amount
                }
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def manage_positions(self):
        """Manage existing positions with stop-loss and take-profit"""
        try:
            for symbol in list(self.active_positions.keys()):
                try:
                    # Get current price
                    ticker = self.client.get_product_ticker(symbol)
                    current_price = float(ticker['price'])
                    
                    # Get crypto balance
                    crypto = symbol.split('-')[0]
                    crypto_balance = self.account_balances.get(crypto, {}).get('available', 0)
                    
                    if crypto_balance <= 0:
                        # Position already closed
                        del self.active_positions[symbol]
                        continue
                    
                    entry_price = self.active_positions[symbol]['entry_price']
                    entry_time = self.active_positions[symbol]['entry_time']
                    
                    # Calculate P&L
                    pnl_pct = (current_price - entry_price) / entry_price
                    
                    # Stop-loss check
                    if pnl_pct <= -Config.STOP_LOSS_PERCENTAGE:
                        logger.info(f"Stop-loss triggered for {symbol} at {current_price}")
                        self.place_order(symbol, 'sell', crypto_balance * current_price)
                        del self.active_positions[symbol]
                    
                    # Take-profit check
                    elif pnl_pct >= Config.TAKE_PROFIT_PERCENTAGE:
                        logger.info(f"Take-profit triggered for {symbol} at {current_price}")
                        self.place_order(symbol, 'sell', crypto_balance * current_price)
                        del self.active_positions[symbol]
                    
                    # Time-based exit (if position held too long)
                    elif datetime.now() - entry_time > timedelta(hours=24):
                        logger.info(f"Time-based exit for {symbol} after 24 hours")
                        self.place_order(symbol, 'sell', crypto_balance * current_price)
                        del self.active_positions[symbol]
                
                except Exception as e:
                    logger.error(f"Error managing position for {symbol}: {e}")
            
        except Exception as e:
            logger.error(f"Error managing positions: {e}")
    
    def execute_trading_cycle(self):
        """Execute one complete trading cycle with safety checks"""
        try:
            logger.info("Starting trading cycle...")
            
            # Check emergency stop
            if self.emergency_stop:
                logger.warning("Trading cycle skipped due to emergency stop")
                return
            
            # Check system health
            if not self.check_system_health():
                logger.warning("System health check failed")
            
            # Check network connectivity
            if not self.check_network_connectivity():
                logger.error("Network connectivity issues. Skipping trading cycle.")
                return
            
            # Check API connectivity
            if not self.check_api_connectivity():
                logger.error("API connectivity issues. Skipping trading cycle.")
                return
            
            # Update account balances
            if not self.check_account_balances():
                logger.error("Failed to check account balances. Skipping trading cycle.")
                return
            
            # Update portfolio value
            self.portfolio_value = self.get_portfolio_value()
            logger.info(f"Current portfolio value: ${self.portfolio_value:.2f}")
            
            # Manage existing positions
            self.manage_positions()
            
            # Analyze each supported pair
            for symbol in Config.SUPPORTED_PAIRS:
                logger.info(f"Analyzing {symbol}...")
                
                # Get market analysis
                analysis = self.analyze_market_conditions(symbol)
                if not analysis:
                    continue
                
                # Log analysis results
                logger.info(f"{symbol} Analysis: {analysis['trend']} trend, "
                          f"Signal strength: {analysis['signal_strength']}, "
                          f"RSI: {analysis['rsi']:.2f}, "
                          f"Price: ${analysis['current_price']:.2f}")
                
                # Check if we should trade
                should_trade, direction = self.should_trade(analysis)
                
                if should_trade:
                    # Calculate position size
                    confidence = analysis['ml_predictions'].get('combined_probability', 0.5) if analysis['ml_predictions'] else 0.5
                    position_size = self.calculate_position_size(symbol, confidence)
                    
                    logger.info(f"Trading signal: {symbol} {direction} ${position_size:.2f}")
                    
                    # Place order
                    order = self.place_order(symbol, direction, position_size)
                    
                    if order and direction == 'buy':
                        # Record position
                        self.active_positions[symbol] = {
                            'entry_price': analysis['current_price'],
                            'entry_time': datetime.now(),
                            'position_size': position_size
                        }
                
                # Add delay between symbols
                time.sleep(2)
            
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            self.consecutive_errors += 1
    
    def reset_daily_counters(self):
        """Reset daily trading counters"""
        self.daily_trades = 0
        logger.info("Daily trading counters reset")
    
    def log_system_status(self):
        """Log comprehensive system status"""
        try:
            uptime = datetime.now() - self.start_time
            logger.info("=" * 60)
            logger.info("SYSTEM STATUS REPORT")
            logger.info("=" * 60)
            logger.info(f"Uptime: {uptime}")
            logger.info(f"Portfolio Value: ${self.portfolio_value:.2f}")
            logger.info(f"Daily Trades: {self.daily_trades}/{Config.MAX_DAILY_TRADES}")
            logger.info(f"Active Positions: {len(self.active_positions)}")
            logger.info(f"Emergency Stop: {self.emergency_stop}")
            logger.info(f"Consecutive Errors: {self.consecutive_errors}")
            logger.info(f"Memory Usage: {self.system_health['memory_usage']:.1f}%")
            logger.info(f"CPU Usage: {self.system_health['cpu_usage']:.1f}%")
            logger.info(f"Network Status: {self.system_health['network_status']}")
            logger.info(f"API Status: {self.system_health['api_status']}")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Error logging system status: {e}")
    
    def run(self):
        """Run the trading engine continuously with 24/7 monitoring"""
        logger.info("Starting TradeX Trading Engine with 24/7 Automation...")
        
        # Load previous system state
        self.load_system_state()
        
        # Schedule daily reset
        schedule.every().day.at("00:00").do(self.reset_daily_counters)
        
        # Schedule system status logging (every 6 hours)
        schedule.every(6).hours.do(self.log_system_status)
        
        # Initial system checks
        if not self.check_system_health():
            logger.warning("Initial system health check failed")
        
        if not self.check_network_connectivity():
            logger.error("Initial network connectivity check failed")
            if not self.attempt_recovery():
                logger.critical("Failed to establish network connectivity. Exiting.")
                return
        
        if not self.check_api_connectivity():
            logger.error("Initial API connectivity check failed")
            if not self.attempt_recovery():
                logger.critical("Failed to establish API connectivity. Exiting.")
                return
        
        # Initial balance check
        if not self.check_account_balances():
            logger.error("Failed initial balance check. Exiting.")
            return
        
        # Initial trading cycle
        self.execute_trading_cycle()
        
        # Schedule regular trading cycles (every hour)
        schedule.every().hour.do(self.execute_trading_cycle)
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Periodic balance check (every 10 minutes)
                if (self.last_balance_check is None or 
                    datetime.now() - self.last_balance_check > timedelta(minutes=10)):
                    self.check_account_balances()
                
                # Periodic system health check (every 5 minutes)
                if (datetime.now() - self.last_heartbeat > timedelta(seconds=self.heartbeat_interval)):
                    self.check_system_health()
                
                # Recovery attempts if needed
                if self.emergency_stop and self.recovery_attempts < self.max_recovery_attempts:
                    if self.attempt_recovery():
                        logger.info("System recovered successfully")
                    else:
                        logger.warning(f"Recovery attempt {self.recovery_attempts} failed")
                        time.sleep(300)  # Wait 5 minutes before next attempt
                
                # Save system state periodically (every hour)
                if datetime.now().minute == 0:
                    self.save_system_state()
                
            except KeyboardInterrupt:
                logger.info("Trading engine stopped by user")
                self.graceful_shutdown()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.consecutive_errors += 1
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.critical("Too many consecutive errors. Emergency stop activated.")
                    self.emergency_stop = True
                    
                    if self.recovery_attempts >= self.max_recovery_attempts:
                        logger.critical("Maximum recovery attempts reached. Exiting.")
                        break
                
                time.sleep(300)  # Wait 5 minutes before retrying
