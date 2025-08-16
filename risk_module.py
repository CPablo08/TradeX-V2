"""
TradeX V3 - Risk Module
Handles stop-loss, take-profit, and dynamic trade sizing
"""

import logging
from datetime import datetime, timedelta
from config import Config

class RiskModule:
    def __init__(self):
        """Initialize Risk Module"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        self.stop_loss_percentage = self.config.STOP_LOSS_PERCENTAGE
        self.take_profit_percentage = self.config.TAKE_PROFIT_PERCENTAGE
        self.max_daily_trades = self.config.MAX_DAILY_TRADES
        self.max_daily_loss = self.config.MAX_DAILY_LOSS
        
        # Trading state
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        self.active_positions = {}
        
        self.logger.info("Risk Module initialized")
    
    def reset_daily_counters(self):
        """Reset daily counters if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
            self.logger.info("Daily counters reset")
    
    def calculate_position_size(self, confidence_score, current_price, available_balance):
        """Calculate dynamic position size based on confidence score"""
        try:
            self.reset_daily_counters()
            
            # Base position size
            base_size = self.config.QUANTITY
            
            # Adjust size based on confidence (0.5 to 1.0)
            confidence_multiplier = 0.5 + (confidence_score - 0.5) * 2
            confidence_multiplier = max(0.5, min(2.0, confidence_multiplier))
            
            # Calculate position size
            position_size = base_size * confidence_multiplier
            
            # Ensure within limits
            position_size = max(self.config.QUANTITY, 
                              min(position_size, self.config.MAX_QUANTITY))
            
            # Check if we have enough balance
            required_balance = position_size * current_price
            if required_balance > available_balance:
                position_size = available_balance / current_price
                self.logger.warning(f"Position size reduced due to insufficient balance")
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return self.config.QUANTITY
    
    def calculate_stop_loss(self, entry_price, side):
        """Calculate stop loss price"""
        try:
            if side == 'BUY':
                stop_loss = entry_price * (1 - self.stop_loss_percentage / 100)
            else:  # SELL
                stop_loss = entry_price * (1 + self.stop_loss_percentage / 100)
            
            return stop_loss
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {e}")
            return None
    
    def calculate_take_profit(self, entry_price, side):
        """Calculate take profit price"""
        try:
            if side == 'BUY':
                take_profit = entry_price * (1 + self.take_profit_percentage / 100)
            else:  # SELL
                take_profit = entry_price * (1 - self.take_profit_percentage / 100)
            
            return take_profit
            
        except Exception as e:
            self.logger.error(f"Error calculating take profit: {e}")
            return None
    
    def can_trade(self, signal_strength):
        """Check if trading is allowed based on risk parameters"""
        try:
            self.reset_daily_counters()
            
            # Check daily trade limit
            if self.daily_trades >= self.max_daily_trades:
                self.logger.warning("Daily trade limit reached")
                return False, "Daily trade limit reached"
            
            # Check daily loss limit
            if self.daily_pnl <= -self.max_daily_loss:
                self.logger.warning("Daily loss limit reached")
                return False, "Daily loss limit reached"
            
            # Check signal strength
            if signal_strength < 0.6:
                self.logger.info("Signal strength too low for trading")
                return False, "Signal strength too low"
            
            return True, "Trading allowed"
            
        except Exception as e:
            self.logger.error(f"Error checking trade permission: {e}")
            return False, f"Error: {e}"
    
    def open_position(self, order_id, side, entry_price, quantity, confidence_score):
        """Record opening of a new position"""
        try:
            stop_loss = self.calculate_stop_loss(entry_price, side)
            take_profit = self.calculate_take_profit(entry_price, side)
            
            position = {
                'order_id': order_id,
                'side': side,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence_score': confidence_score,
                'entry_time': datetime.now(),
                'status': 'OPEN'
            }
            
            self.active_positions[order_id] = position
            self.daily_trades += 1
            
            self.logger.info(f"Position opened: {side} {quantity} BTC at {entry_price}")
            return position
            
        except Exception as e:
            self.logger.error(f"Error opening position: {e}")
            return None
    
    def close_position(self, order_id, exit_price, pnl):
        """Record closing of a position"""
        try:
            if order_id in self.active_positions:
                position = self.active_positions[order_id]
                position['exit_price'] = exit_price
                position['pnl'] = pnl
                position['exit_time'] = datetime.now()
                position['status'] = 'CLOSED'
                
                # Update daily PnL
                self.daily_pnl += pnl
                
                # Remove from active positions
                del self.active_positions[order_id]
                
                self.logger.info(f"Position closed: PnL = {pnl:.4f}")
                return position
            else:
                self.logger.warning(f"Position {order_id} not found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error closing position: {e}")
            return None
    
    def check_stop_loss_take_profit(self, current_price):
        """Check if any positions hit stop loss or take profit"""
        try:
            positions_to_close = []
            
            for order_id, position in self.active_positions.items():
                if position['status'] != 'OPEN':
                    continue
                
                side = position['side']
                entry_price = position['entry_price']
                stop_loss = position['stop_loss']
                take_profit = position['take_profit']
                
                # Check stop loss
                if side == 'BUY' and current_price <= stop_loss:
                    positions_to_close.append({
                        'order_id': order_id,
                        'reason': 'STOP_LOSS',
                        'exit_price': stop_loss
                    })
                elif side == 'SELL' and current_price >= stop_loss:
                    positions_to_close.append({
                        'order_id': order_id,
                        'reason': 'STOP_LOSS',
                        'exit_price': stop_loss
                    })
                
                # Check take profit
                elif side == 'BUY' and current_price >= take_profit:
                    positions_to_close.append({
                        'order_id': order_id,
                        'reason': 'TAKE_PROFIT',
                        'exit_price': take_profit
                    })
                elif side == 'SELL' and current_price <= take_profit:
                    positions_to_close.append({
                        'order_id': order_id,
                        'reason': 'TAKE_PROFIT',
                        'exit_price': take_profit
                    })
            
            return positions_to_close
            
        except Exception as e:
            self.logger.error(f"Error checking stop loss/take profit: {e}")
            return []
    
    def get_risk_metrics(self):
        """Get current risk metrics"""
        try:
            self.reset_daily_counters()
            
            return {
                'daily_trades': self.daily_trades,
                'max_daily_trades': self.max_daily_trades,
                'daily_pnl': self.daily_pnl,
                'max_daily_loss': self.max_daily_loss,
                'active_positions': len(self.active_positions),
                'stop_loss_percentage': self.stop_loss_percentage,
                'take_profit_percentage': self.take_profit_percentage,
                'max_concurrent_positions': getattr(self.config, 'MAX_CONCURRENT_POSITIONS', 3),
                'correlation_limit': getattr(self.config, 'CORRELATION_LIMIT', 0.7)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk metrics: {e}")
            return {}
    
    def calculate_position_size(self, confidence, current_price, win_rate=None, avg_win=None, avg_loss=None):
        """Calculate optimal position size using Kelly Criterion and volatility adjustment"""
        try:
            # Base position size
            base_size = getattr(self.config, 'BASE_POSITION_SIZE', 0.02)
            
            # Kelly Criterion calculation
            if getattr(self.config, 'KELLY_CRITERION', False) and win_rate and avg_win and avg_loss:
                kelly_fraction = self._calculate_kelly_criterion(win_rate, avg_win, avg_loss)
                kelly_size = base_size * kelly_fraction
            else:
                kelly_size = base_size
            
            # Volatility adjustment
            if getattr(self.config, 'VOLATILITY_ADJUSTMENT', False):
                volatility_factor = self._calculate_volatility_factor()
                volatility_size = kelly_size * volatility_factor
            else:
                volatility_size = kelly_size
            
            # Confidence adjustment
            confidence_multiplier = min(confidence, 1.0)
            adjusted_size = volatility_size * confidence_multiplier
            
            # Ensure within limits
            max_size = getattr(self.config, 'MAX_POSITION_SIZE', 0.10)
            final_size = min(adjusted_size, max_size)
            final_size = max(final_size, self.config.QUANTITY)  # Minimum size
            
            return final_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return self.config.QUANTITY
    
    def _calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        """Calculate Kelly Criterion fraction"""
        try:
            if avg_loss == 0:
                return 0.5  # Default to 50% if no loss data
            
            # Kelly formula: f = (bp - q) / b
            # where b = odds received, p = probability of win, q = probability of loss
            b = avg_win / abs(avg_loss)  # Odds received
            p = win_rate / 100  # Probability of win
            q = 1 - p  # Probability of loss
            
            kelly_fraction = (b * p - q) / b
            
            # Limit Kelly fraction to reasonable bounds
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Max 25% per trade
            
            return kelly_fraction
            
        except Exception as e:
            self.logger.error(f"Error calculating Kelly Criterion: {e}")
            return 0.5
    
    def _calculate_volatility_factor(self):
        """Calculate volatility adjustment factor"""
        try:
            # Get recent volatility data
            recent_volatility = self._get_recent_volatility()
            
            if recent_volatility is None:
                return 1.0
            
            # Adjust position size inversely to volatility
            # Higher volatility = smaller position size
            volatility_factor = 1.0 / (1.0 + recent_volatility)
            
            # Limit the factor
            volatility_factor = max(0.5, min(volatility_factor, 1.5))
            
            return volatility_factor
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility factor: {e}")
            return 1.0
    
    def _get_recent_volatility(self):
        """Get recent market volatility"""
        try:
            # This would typically get volatility from market data
            # For now, return a default value
            return 0.02  # 2% volatility
            
        except Exception as e:
            self.logger.error(f"Error getting volatility: {e}")
            return None
    
    def should_pause_trading(self, volatility=None):
        """Check if trading should be paused due to high volatility"""
        try:
            # Simple volatility check (can be enhanced)
            if volatility and volatility > 0.05:  # 5% volatility threshold
                self.logger.warning("Trading paused due to high volatility")
                return True, "High volatility detected"
            
            return False, "Trading allowed"
            
        except Exception as e:
            self.logger.error(f"Error checking pause condition: {e}")
            return False, f"Error: {e}"
    
    def get_position_summary(self):
        """Get summary of all positions"""
        try:
            summary = {
                'total_positions': len(self.active_positions),
                'open_positions': len([p for p in self.active_positions.values() if p['status'] == 'OPEN']),
                'total_value': sum(p['quantity'] * p['entry_price'] for p in self.active_positions.values()),
                'average_confidence': sum(p['confidence_score'] for p in self.active_positions.values()) / len(self.active_positions) if self.active_positions else 0
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting position summary: {e}")
            return {}
