#!/usr/bin/env python3
"""
TradeX Backtesting Engine
Tests the entire trading system with real historical data from Coinbase
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
import json
import matplotlib.pyplot as plt
import seaborn as sns
import time
import threading
from data_collector import DataCollector
from ml_engine import MLEngine
from risk_manager import RiskManager
from config import Config

class BacktestEngine:
    def __init__(self, start_date=None, end_date=None, initial_balance=1000):
        self.start_date = start_date or (datetime.now() - timedelta(days=30))
        self.end_date = end_date or datetime.now()
        self.initial_balance = initial_balance
        
        # Initialize components
        self.data_collector = DataCollector()
        self.ml_engine = MLEngine()
        self.risk_manager = RiskManager()
        
        # Backtest state
        self.current_balance = initial_balance
        self.positions = {}
        self.trades = []
        self.daily_balances = []
        self.trade_history = []
        self.performance_metrics = {}
        
        # Loading animation
        self.loading_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.loading_index = 0
        self.is_loading = False
        self.loading_thread = None
        
        # Load ML models
        self.ml_engine.load_models()
        
        # Setup logging
        logger.add("backtest.log", rotation="1 day", retention="7 days")
    
    def start_loading(self, message="Loading"):
        """Start loading animation"""
        self.is_loading = True
        self.loading_message = message
        self.loading_thread = threading.Thread(target=self._loading_animation)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def stop_loading(self):
        """Stop loading animation"""
        self.is_loading = False
        if self.loading_thread:
            self.loading_thread.join(timeout=1)
        print("\r" + " " * 80 + "\r", end="", flush=True)  # Clear loading line
    
    def _loading_animation(self):
        """Loading animation thread"""
        while self.is_loading:
            char = self.loading_chars[self.loading_index]
            print(f"\r{char} {self.loading_message}...", end="", flush=True)
            self.loading_index = (self.loading_index + 1) % len(self.loading_chars)
            time.sleep(0.1)
        
    def fetch_historical_data(self, symbol, start_date, end_date):
        """Fetch historical data for backtesting"""
        try:
            self.start_loading(f"Fetching {symbol} data")
            logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
            
            # Calculate days difference
            days_diff = (end_date - start_date).days
            
            # Fetch data with extra buffer for technical indicators
            df = self.data_collector.fetch_historical_data(
                symbol, 
                lookback_days=days_diff + 50  # Extra buffer for indicators
            )
            
            self.stop_loading()
            
            if df is None:
                logger.error(f"Failed to fetch data for {symbol}")
                return None
            
            # Filter to date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            # Calculate technical indicators
            self.start_loading("Calculating technical indicators")
            df = self.data_collector.calculate_technical_indicators(df)
            self.stop_loading()
            
            # Identify patterns
            self.start_loading("Identifying chart patterns")
            patterns = self.data_collector.identify_chart_patterns(df)
            self.stop_loading()
            
            logger.info(f"Fetched {len(df)} data points for {symbol}")
            return df, patterns
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None, {}
    
    def simulate_market_conditions(self, df, patterns, symbol):
        """Simulate market analysis for a given timestamp"""
        try:
            # Prepare features for ML
            features_df = self.ml_engine.prepare_features(df, patterns)
            if features_df is None:
                return None
            
            # Get ML predictions
            ml_predictions = self.ml_engine.predict(features_df)
            
            # Technical analysis signals
            current = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else current
            
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
                'timestamp': current.name,
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
            logger.error(f"Error simulating market conditions: {e}")
            return None
    
    def should_trade(self, analysis):
        """Determine if we should trade based on analysis"""
        if not analysis:
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
        
        # Determine trade direction
        if analysis['bullish_signals'] > analysis['bearish_signals']:
            return True, 'buy'
        elif analysis['bearish_signals'] > analysis['bullish_signals']:
            return True, 'sell'
        
        return False, None
    
    def execute_trade(self, symbol, side, price, timestamp, amount_usd):
        """Execute a trade in the backtest"""
        try:
            # Calculate position size
            trade_amount = min(amount_usd, self.current_balance * Config.MAX_POSITION_SIZE)
            
            if side == 'buy':
                # Check if we have enough balance
                if trade_amount > self.current_balance:
                    return False
                
                # Calculate crypto amount
                crypto_amount = trade_amount / price
                
                # Update balance
                self.current_balance -= trade_amount
                
                # Add position
                if symbol not in self.positions:
                    self.positions[symbol] = {
                        'amount': crypto_amount,
                        'entry_price': price,
                        'entry_time': timestamp,
                        'total_invested': trade_amount
                    }
                else:
                    # Average down/up
                    total_amount = self.positions[symbol]['amount'] + crypto_amount
                    total_invested = self.positions[symbol]['total_invested'] + trade_amount
                    avg_price = total_invested / total_amount
                    
                    self.positions[symbol] = {
                        'amount': total_amount,
                        'entry_price': avg_price,
                        'entry_time': timestamp,
                        'total_invested': total_invested
                    }
                
                trade_type = 'BUY'
                
            elif side == 'sell':
                # Check if we have position to sell
                if symbol not in self.positions or self.positions[symbol]['amount'] <= 0:
                    return False
                
                # Calculate sell amount
                position = self.positions[symbol]
                sell_amount = min(position['amount'], trade_amount / price)
                
                # Calculate proceeds
                proceeds = sell_amount * price
                
                # Update balance
                self.current_balance += proceeds
                
                # Update position
                remaining_amount = position['amount'] - sell_amount
                if remaining_amount <= 0:
                    del self.positions[symbol]
                else:
                    self.positions[symbol]['amount'] = remaining_amount
                
                trade_type = 'SELL'
            
            # Record trade
            trade_record = {
                'timestamp': timestamp,
                'symbol': symbol,
                'side': side,
                'price': price,
                'amount_usd': trade_amount,
                'balance_after': self.current_balance,
                'trade_type': trade_type
            }
            
            self.trades.append(trade_record)
            
            # Calculate P&L for sells
            if side == 'sell' and symbol in self.positions:
                entry_price = self.positions[symbol]['entry_price']
                pnl_pct = (price - entry_price) / entry_price
                trade_record['pnl_pct'] = pnl_pct
                trade_record['pnl_usd'] = sell_amount * (price - entry_price)
            
            logger.info(f"Backtest Trade: {trade_type} {symbol} at ${price:.2f} - Amount: ${trade_amount:.2f} - Balance: ${self.current_balance:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def check_stop_loss_take_profit(self, symbol, current_price, timestamp):
        """Check stop-loss and take-profit for positions"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Stop-loss check
        if pnl_pct <= -Config.STOP_LOSS_PERCENTAGE:
            logger.info(f"Stop-loss triggered for {symbol} at ${current_price:.2f}")
            self.execute_trade(symbol, 'sell', current_price, timestamp, position['total_invested'])
        
        # Take-profit check
        elif pnl_pct >= Config.TAKE_PROFIT_PERCENTAGE:
            logger.info(f"Take-profit triggered for {symbol} at ${current_price:.2f}")
            self.execute_trade(symbol, 'sell', current_price, timestamp, position['total_invested'])
    
    def run_backtest(self):
        """Run the complete backtest"""
        print("\n" + "="*80)
        print("🚀 STARTING TRADEX BACKTEST")
        print("="*80)
        print(f"📅 Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"💰 Initial Balance: ${self.initial_balance:,.2f}")
        print(f"📊 Testing: {', '.join(Config.SUPPORTED_PAIRS)}")
        print("="*80)
        
        logger.info("🚀 Starting TradeX Backtest...")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Initial Balance: ${self.initial_balance:,.2f}")
        
        # Track daily balances
        self.daily_balances = [{'date': self.start_date, 'balance': self.initial_balance}]
        
        # Fetch historical data for all symbols
        all_data = {}
        all_patterns = {}
        
        print("\n📊 FETCHING MARKET DATA...")
        for symbol in Config.SUPPORTED_PAIRS:
            df, patterns = self.fetch_historical_data(symbol, self.start_date, self.end_date)
            if df is not None:
                all_data[symbol] = df
                all_patterns[symbol] = patterns
        
        if not all_data:
            logger.error("No historical data available for backtesting")
            print("❌ No historical data available for backtesting")
            return
        
        # Get all unique timestamps
        all_timestamps = set()
        for df in all_data.values():
            all_timestamps.update(df.index)
        
        all_timestamps = sorted(list(all_timestamps))
        
        logger.info(f"Running backtest on {len(all_timestamps)} timestamps")
        print(f"✅ Data loaded: {len(all_timestamps)} timestamps")
        print(f"📈 Starting backtest simulation...\n")
        
        # Main backtest loop
        for i, timestamp in enumerate(all_timestamps):
            try:
                # Update daily balance
                if i % 24 == 0:  # Every 24 hours (assuming hourly data)
                    self.daily_balances.append({
                        'date': timestamp,
                        'balance': self.current_balance
                    })
                
                # Process each symbol
                for symbol in Config.SUPPORTED_PAIRS:
                    if symbol not in all_data:
                        continue
                    
                    df = all_data[symbol]
                    
                    # Get data up to current timestamp
                    current_data = df[df.index <= timestamp]
                    if len(current_data) < 50:  # Need enough data for indicators
                        continue
                    
                    # Get current price
                    current_price = current_data.iloc[-1]['close']
                    
                    # Check stop-loss/take-profit for existing positions
                    self.check_stop_loss_take_profit(symbol, current_price, timestamp)
                    
                    # Simulate market analysis
                    analysis = self.simulate_market_conditions(current_data, all_patterns[symbol], symbol)
                    if not analysis:
                        continue
                    
                    # Check if we should trade
                    should_trade, direction = self.should_trade(analysis)
                    
                    if should_trade:
                        # Calculate position size
                        trade_amount = Config.TRADE_AMOUNT_USD
                        
                        # Execute trade
                        self.execute_trade(symbol, direction, current_price, timestamp, trade_amount)
                
                # Progress update
                if i % 100 == 0:
                    progress = (i / len(all_timestamps)) * 100
                    logger.info(f"Backtest Progress: {progress:.1f}% - Balance: ${self.current_balance:.2f}")
                    print(f"🔄 Progress: {progress:.1f}% | Balance: ${self.current_balance:.2f}")
                
            except Exception as e:
                logger.error(f"Error in backtest loop at {timestamp}: {e}")
                continue
        
        # Close any remaining positions at end price
        for symbol in list(self.positions.keys()):
            if symbol in all_data:
                end_price = all_data[symbol].iloc[-1]['close']
                position = self.positions[symbol]
                self.execute_trade(symbol, 'sell', end_price, self.end_date, position['total_invested'])
        
        # Calculate performance metrics
        print("\n📊 CALCULATING PERFORMANCE METRICS...")
        self.start_loading("Calculating performance metrics")
        self.calculate_performance_metrics()
        self.stop_loading()
        
        # Generate reports
        print("\n📁 GENERATING REPORTS...")
        self.start_loading("Generating reports and plots")
        self.generate_reports()
        self.stop_loading()
        
        logger.info("✅ Backtest completed!")
        print("\n✅ BACKTEST COMPLETED!")
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        try:
            # Basic metrics
            final_balance = self.current_balance
            total_return = final_balance - self.initial_balance
            total_return_pct = (total_return / self.initial_balance) * 100
            
            # Trade metrics
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t.get('pnl_usd', 0) > 0])
            losing_trades = len([t for t in self.trades if t.get('pnl_usd', 0) < 0])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # P&L metrics
            total_pnl = sum([t.get('pnl_usd', 0) for t in self.trades])
            avg_win = np.mean([t.get('pnl_usd', 0) for t in self.trades if t.get('pnl_usd', 0) > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t.get('pnl_usd', 0) for t in self.trades if t.get('pnl_usd', 0) < 0]) if losing_trades > 0 else 0
            
            # Risk metrics
            daily_returns = []
            for i in range(1, len(self.daily_balances)):
                prev_balance = self.daily_balances[i-1]['balance']
                curr_balance = self.daily_balances[i]['balance']
                daily_return = (curr_balance - prev_balance) / prev_balance
                daily_returns.append(daily_return)
            
            volatility = np.std(daily_returns) * np.sqrt(365) if daily_returns else 0
            sharpe_ratio = (np.mean(daily_returns) * 365) / volatility if volatility > 0 else 0
            
            # Maximum drawdown
            peak_balance = self.initial_balance
            max_drawdown = 0
            
            for balance_data in self.daily_balances:
                balance = balance_data['balance']
                if balance > peak_balance:
                    peak_balance = balance
                drawdown = (peak_balance - balance) / peak_balance
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Store metrics
            self.performance_metrics = {
                'initial_balance': self.initial_balance,
                'final_balance': final_balance,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'profit_factor': abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else float('inf')
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
    
    def generate_reports(self):
        """Generate comprehensive backtest reports"""
        try:
            # Create reports directory
            os.makedirs('backtest_reports', exist_ok=True)
            
            # Save performance metrics
            with open('backtest_reports/performance_metrics.json', 'w') as f:
                json.dump(self.performance_metrics, f, indent=2, default=str)
            
            # Save trade history
            trades_df = pd.DataFrame(self.trades)
            if not trades_df.empty:
                trades_df.to_csv('backtest_reports/trade_history.csv', index=False)
            
            # Save daily balances
            balances_df = pd.DataFrame(self.daily_balances)
            balances_df.to_csv('backtest_reports/daily_balances.csv', index=False)
            
            # Generate plots
            self.generate_plots()
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
    
    def generate_plots(self):
        """Generate performance visualization plots"""
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('TradeX Backtest Results', fontsize=16, fontweight='bold')
            
            # 1. Portfolio Value Over Time
            balances_df = pd.DataFrame(self.daily_balances)
            balances_df['date'] = pd.to_datetime(balances_df['date'])
            
            axes[0, 0].plot(balances_df['date'], balances_df['balance'], linewidth=2, color='blue')
            axes[0, 0].axhline(y=self.initial_balance, color='red', linestyle='--', alpha=0.7, label='Initial Balance')
            axes[0, 0].set_title('Portfolio Value Over Time')
            axes[0, 0].set_xlabel('Date')
            axes[0, 0].set_ylabel('Portfolio Value ($)')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Trade P&L Distribution
            if self.trades:
                trades_df = pd.DataFrame(self.trades)
                pnl_values = [t.get('pnl_usd', 0) for t in self.trades if 'pnl_usd' in t]
                
                if pnl_values:
                    axes[0, 1].hist(pnl_values, bins=20, alpha=0.7, color='green', edgecolor='black')
                    axes[0, 1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
                    axes[0, 1].set_title('Trade P&L Distribution')
                    axes[0, 1].set_xlabel('P&L ($)')
                    axes[0, 1].set_ylabel('Number of Trades')
                    axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Win/Loss Ratio
            if self.performance_metrics['total_trades'] > 0:
                labels = ['Winning Trades', 'Losing Trades']
                sizes = [self.performance_metrics['winning_trades'], self.performance_metrics['losing_trades']]
                colors = ['lightgreen', 'lightcoral']
                
                axes[1, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                axes[1, 0].set_title('Win/Loss Ratio')
            
            # 4. Daily Returns
            if len(self.daily_balances) > 1:
                daily_returns = []
                dates = []
                
                for i in range(1, len(self.daily_balances)):
                    prev_balance = self.daily_balances[i-1]['balance']
                    curr_balance = self.daily_balances[i]['balance']
                    daily_return = (curr_balance - prev_balance) / prev_balance * 100
                    daily_returns.append(daily_return)
                    dates.append(self.daily_balances[i]['date'])
                
                axes[1, 1].bar(range(len(daily_returns)), daily_returns, alpha=0.7, color='skyblue')
                axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
                axes[1, 1].set_title('Daily Returns (%)')
                axes[1, 1].set_xlabel('Day')
                axes[1, 1].set_ylabel('Return (%)')
                axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('backtest_reports/performance_plots.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("📊 Performance plots generated")
            
        except Exception as e:
            logger.error(f"Error generating plots: {e}")
    
    def print_summary(self):
        """Print comprehensive backtest summary"""
        try:
            metrics = self.performance_metrics
            
            print("\n" + "="*80)
            print("📊 TRADEX BACKTEST RESULTS")
            print("="*80)
            print(f"📅 Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
            print(f"💰 Initial Balance: ${metrics['initial_balance']:,.2f}")
            print(f"💰 Final Balance: ${metrics['final_balance']:,.2f}")
            print(f"📈 Total Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")
            print()
            
            print("📊 TRADING METRICS:")
            print(f"   🔄 Total Trades: {metrics['total_trades']}")
            print(f"   ✅ Winning Trades: {metrics['winning_trades']}")
            print(f"   ❌ Losing Trades: {metrics['losing_trades']}")
            print(f"   🎯 Win Rate: {metrics['win_rate']:.1f}%")
            print(f"   💵 Total P&L: ${metrics['total_pnl']:,.2f}")
            print(f"   📈 Average Win: ${metrics['avg_win']:,.2f}")
            print(f"   📉 Average Loss: ${metrics['avg_loss']:,.2f}")
            print(f"   ⚖️  Profit Factor: {metrics['profit_factor']:.2f}")
            print()
            
            print("📊 RISK METRICS:")
            print(f"   📊 Volatility: {metrics['volatility']:.2f}")
            print(f"   📈 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"   📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print()
            
            print("📁 REPORTS SAVED TO:")
            print("   📄 backtest_reports/performance_metrics.json")
            print("   📄 backtest_reports/trade_history.csv")
            print("   📄 backtest_reports/daily_balances.csv")
            print("   📊 backtest_reports/performance_plots.png")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")

def main():
    """Main backtest function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='TradeX Backtest Engine')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--initial-balance', type=float, default=10000, help='Initial balance')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    # Run backtest
    backtest = BacktestEngine(
        start_date=start_date,
        end_date=end_date,
        initial_balance=args.initial_balance
    )
    
    backtest.run_backtest()

if __name__ == "__main__":
    main()
