"""
TradeX V3 - Trade Log & Analytics Module
Stores every trade, PnL, and metrics for performance review
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
from config import Config

class TradeLogger:
    def __init__(self):
        """Initialize Trade Logger"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.db_path = self.config.DATABASE_PATH
        
        # Initialize database
        self.init_database()
        
        self.logger.info("Trade Logger initialized")
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    entry_price REAL,
                    exit_price REAL,
                    pnl REAL,
                    pnl_percentage REAL,
                    confidence_score REAL,
                    decision_reason TEXT,
                    entry_time TIMESTAMP,
                    exit_time TIMESTAMP,
                    status TEXT,
                    stop_loss REAL,
                    take_profit REAL,
                    execution_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create decisions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    decision TEXT,
                    confidence REAL,
                    reason TEXT,
                    technical_signal TEXT,
                    ml_signal TEXT,
                    trend_signal TEXT,
                    liquidity_signal TEXT,
                    current_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create performance_metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    total_pnl REAL,
                    win_rate REAL,
                    avg_win REAL,
                    avg_loss REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def log_trade(self, order_data, decision_data=None):
        """Log a new trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract order data
            order_id = order_data.get('orderId', '')
            symbol = order_data.get('symbol', '')
            side = order_data.get('side', '')
            quantity = float(order_data.get('quantity', 0))
            entry_price = float(order_data.get('price', 0))
            execution_time = order_data.get('execution_time', datetime.now())
            
            # Extract decision data if available
            confidence_score = 0.5
            decision_reason = "No decision data"
            if decision_data:
                confidence_score = decision_data.get('confidence', 0.5)
                decision_reason = decision_data.get('reason', 'No reason provided')
            
            # Calculate stop loss and take profit
            stop_loss = None
            take_profit = None
            if side == 'BUY':
                stop_loss = entry_price * (1 - self.config.STOP_LOSS_PERCENTAGE / 100)
                take_profit = entry_price * (1 + self.config.TAKE_PROFIT_PERCENTAGE / 100)
            elif side == 'SELL':
                stop_loss = entry_price * (1 + self.config.STOP_LOSS_PERCENTAGE / 100)
                take_profit = entry_price * (1 - self.config.TAKE_PROFIT_PERCENTAGE / 100)
            
            # Insert trade record
            cursor.execute('''
                INSERT INTO trades (
                    order_id, symbol, side, quantity, entry_price, 
                    confidence_score, decision_reason, entry_time, 
                    status, stop_loss, take_profit, execution_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, symbol, side, quantity, entry_price,
                confidence_score, decision_reason, execution_time,
                'OPEN', stop_loss, take_profit, execution_time
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Trade logged: {side} {quantity} {symbol} at {entry_price}")
            
        except Exception as e:
            self.logger.error(f"Error logging trade: {e}")
    
    def close_trade(self, order_id, exit_price, pnl, exit_reason="Manual"):
        """Close a trade and calculate PnL"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get trade details
            cursor.execute('SELECT * FROM trades WHERE order_id = ?', (order_id,))
            trade = cursor.fetchone()
            
            if not trade:
                self.logger.warning(f"Trade not found: {order_id}")
                return False
            
            # Calculate PnL percentage
            entry_price = trade[5]  # entry_price column
            pnl_percentage = (pnl / (entry_price * trade[4])) * 100  # quantity * entry_price
            
            # Update trade record
            cursor.execute('''
                UPDATE trades SET 
                    exit_price = ?, pnl = ?, pnl_percentage = ?,
                    exit_time = ?, status = ?
                WHERE order_id = ?
            ''', (exit_price, pnl, pnl_percentage, datetime.now(), 'CLOSED', order_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Trade closed: {order_id}, PnL: {pnl:.4f} ({pnl_percentage:.2f}%)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing trade: {e}")
            return False
    
    def log_decision(self, decision_data, market_data):
        """Log a trading decision"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract decision data
            decision = decision_data.get('decision', 'HOLD')
            confidence = decision_data.get('confidence', 0.5)
            reason = decision_data.get('reason', 'No reason')
            current_price = market_data.get('current_price', 0)
            
            # Extract signal breakdown
            signal_breakdown = decision_data.get('signal_breakdown', {})
            technical_signal = signal_breakdown.get('technical', {}).get('signal', 'N/A')
            ml_signal = signal_breakdown.get('ml', {}).get('signal', 'N/A')
            trend_signal = signal_breakdown.get('trend', {}).get('signal', 'N/A')
            liquidity_signal = signal_breakdown.get('liquidity', {}).get('signal', 'N/A')
            
            # Insert decision record
            cursor.execute('''
                INSERT INTO decisions (
                    timestamp, decision, confidence, reason, technical_signal,
                    ml_signal, trend_signal, liquidity_signal, current_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(), decision, confidence, reason, technical_signal,
                ml_signal, trend_signal, liquidity_signal, current_price
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging decision: {e}")
    
    def get_trade_history(self, days=30):
        """Get trade history for the specified number of days"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get trades from the last N days
            start_date = datetime.now() - timedelta(days=days)
            
            query = '''
                SELECT * FROM trades 
                WHERE created_at >= ? 
                ORDER BY created_at DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(start_date,))
            conn.close()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting trade history: {e}")
            return pd.DataFrame()
    
    def calculate_performance_metrics(self, days=30):
        """Calculate comprehensive performance metrics for the specified period"""
        try:
            df = self.get_trade_history(days)
            
            if df.empty:
                return {}
            
            # Filter closed trades
            closed_trades = df[df['status'] == 'CLOSED']
            
            if closed_trades.empty:
                return {}
            
            # Calculate basic metrics
            total_trades = len(closed_trades)
            winning_trades = len(closed_trades[closed_trades['pnl'] > 0])
            losing_trades = len(closed_trades[closed_trades['pnl'] < 0])
            
            total_pnl = closed_trades['pnl'].sum()
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            avg_win = closed_trades[closed_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = closed_trades[closed_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            
            # Calculate max drawdown
            cumulative_pnl = closed_trades['pnl'].cumsum()
            running_max = cumulative_pnl.expanding().max()
            drawdown = (cumulative_pnl - running_max) / running_max * 100
            max_drawdown = abs(drawdown.min())
            
            # Calculate Sharpe ratio
            if len(closed_trades) > 1:
                returns = closed_trades['pnl_percentage'] / 100
                sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calculate additional metrics
            calmar_ratio = self._calculate_calmar_ratio(closed_trades, total_pnl, max_drawdown)
            sortino_ratio = self._calculate_sortino_ratio(closed_trades)
            regime_metrics = self._calculate_regime_metrics(closed_trades)
            risk_metrics = self._calculate_risk_metrics(closed_trades)
            
            metrics = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'calmar_ratio': calmar_ratio,
                'sortino_ratio': sortino_ratio,
                'profit_factor': abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else float('inf'),
                'regime_metrics': regime_metrics,
                'risk_metrics': risk_metrics
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _calculate_calmar_ratio(self, trades_df, total_pnl, max_drawdown):
        """Calculate Calmar ratio"""
        try:
            if max_drawdown == 0:
                return 0
            
            # Annualized return / max drawdown
            days = (trades_df['created_at'].max() - trades_df['created_at'].min()).days
            if days == 0:
                return 0
            
            annualized_return = (total_pnl / days) * 365
            calmar_ratio = annualized_return / max_drawdown
            
            return calmar_ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating Calmar ratio: {e}")
            return 0
    
    def _calculate_sortino_ratio(self, trades_df):
        """Calculate Sortino ratio"""
        try:
            if trades_df.empty or len(trades_df) < 2:
                return 0
            
            returns = trades_df['pnl_percentage'] / 100
            avg_return = returns.mean()
            negative_returns = returns[returns < 0]
            
            if len(negative_returns) == 0:
                return 0
            
            downside_deviation = negative_returns.std()
            
            if downside_deviation == 0:
                return 0
            
            sortino = avg_return / downside_deviation
            return sortino
            
        except Exception as e:
            self.logger.error(f"Error calculating Sortino ratio: {e}")
            return 0
    
    def _calculate_regime_metrics(self, trades_df):
        """Calculate performance metrics by market regime"""
        try:
            if trades_df.empty:
                return {}
            
            regime_metrics = {}
            
            # Group by market regime if available
            if 'market_regime' in trades_df.columns:
                for regime in trades_df['market_regime'].unique():
                    if pd.isna(regime):
                        continue
                    
                    regime_trades = trades_df[trades_df['market_regime'] == regime]
                    
                    if len(regime_trades) > 0:
                        regime_metrics[regime] = {
                            'trades': len(regime_trades),
                            'win_rate': (len(regime_trades[regime_trades['pnl'] > 0]) / len(regime_trades)) * 100,
                            'avg_pnl': regime_trades['pnl'].mean(),
                            'total_pnl': regime_trades['pnl'].sum()
                        }
            
            return regime_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating regime metrics: {e}")
            return {}
    
    def _calculate_risk_metrics(self, trades_df):
        """Calculate additional risk metrics"""
        try:
            if trades_df.empty:
                return {}
            
            # Value at Risk (VaR)
            returns = trades_df['pnl_percentage'] / 100
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
            
            # Expected Shortfall (Conditional VaR)
            es_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else 0
            
            # Maximum consecutive losses
            consecutive_losses = self._calculate_consecutive_losses(trades_df)
            
            return {
                'var_95': var_95,
                'expected_shortfall_95': es_95,
                'max_consecutive_losses': consecutive_losses
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def _calculate_consecutive_losses(self, trades_df):
        """Calculate maximum consecutive losses"""
        try:
            if trades_df.empty:
                return 0
            
            # Create sequence of wins/losses
            wins_losses = (trades_df['pnl'] > 0).astype(int)
            
            # Find consecutive losses
            consecutive_losses = 0
            max_consecutive_losses = 0
            
            for result in wins_losses:
                if result == 0:  # Loss
                    consecutive_losses += 1
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
                else:  # Win
                    consecutive_losses = 0
            
            return max_consecutive_losses
            
        except Exception as e:
            self.logger.error(f"Error calculating consecutive losses: {e}")
            return 0
    
    def get_recent_decisions(self, limit=50):
        """Get recent trading decisions"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM decisions 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting recent decisions: {e}")
            return pd.DataFrame()
    
    def export_trades_to_csv(self, filename=None):
        """Export trades to CSV file"""
        try:
            if filename is None:
                filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            df = self.get_trade_history(days=365)  # Export last year
            df.to_csv(filename, index=False)
            
            self.logger.info(f"Trades exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting trades: {e}")
            return None
    
    def get_daily_summary(self, date=None):
        """Get trading summary for a specific date"""
        try:
            if date is None:
                date = datetime.now().date()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get trades for the date
            cursor.execute('''
                SELECT * FROM trades 
                WHERE DATE(created_at) = ?
            ''', (date,))
            
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return {
                    'date': date,
                    'total_trades': 0,
                    'total_pnl': 0,
                    'win_rate': 0
                }
            
            # Calculate summary
            total_trades = len(trades)
            closed_trades = [t for t in trades if t[13] == 'CLOSED']  # status column
            total_pnl = sum(t[7] for t in closed_trades if t[7] is not None)  # pnl column
            winning_trades = len([t for t in closed_trades if t[7] and t[7] > 0])
            win_rate = (winning_trades / len(closed_trades)) * 100 if closed_trades else 0
            
            return {
                'date': date,
                'total_trades': total_trades,
                'closed_trades': len(closed_trades),
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'winning_trades': winning_trades
            }
            
        except Exception as e:
            self.logger.error(f"Error getting daily summary: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep=90):
        """Clean up old data to keep database size manageable"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old trades
            cursor.execute('DELETE FROM trades WHERE created_at < ?', (cutoff_date,))
            trades_deleted = cursor.rowcount
            
            # Delete old decisions
            cursor.execute('DELETE FROM decisions WHERE created_at < ?', (cutoff_date,))
            decisions_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up {trades_deleted} old trades and {decisions_deleted} old decisions")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
