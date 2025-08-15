import pandas as pd
import numpy as np
from loguru import logger
from config import Config
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self):
        self.max_drawdown = Config.MAX_DRAWDOWN
        self.correlation_threshold = Config.CORRELATION_THRESHOLD
        self.position_history = []
        self.portfolio_history = []
        
    def calculate_correlation(self, btc_data, eth_data):
        """Calculate correlation between BTC and ETH returns"""
        try:
            if btc_data is None or eth_data is None:
                return 0
            
            # Calculate returns
            btc_returns = btc_data['close'].pct_change().dropna()
            eth_returns = eth_data['close'].pct_change().dropna()
            
            # Align data
            min_length = min(len(btc_returns), len(eth_returns))
            btc_returns = btc_returns.tail(min_length)
            eth_returns = eth_returns.tail(min_length)
            
            # Calculate correlation
            correlation = btc_returns.corr(eth_returns)
            
            return correlation if not np.isnan(correlation) else 0
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0
    
    def check_correlation_risk(self, btc_data, eth_data):
        """Check if correlation is too high for safe trading"""
        correlation = self.calculate_correlation(btc_data, eth_data)
        
        if abs(correlation) > self.correlation_threshold:
            logger.warning(f"High correlation detected: {correlation:.3f}. Consider reducing position sizes.")
            return True, correlation
        
        return False, correlation
    
    def calculate_drawdown(self, portfolio_values):
        """Calculate current drawdown"""
        if len(portfolio_values) < 2:
            return 0
        
        peak = max(portfolio_values)
        current = portfolio_values[-1]
        drawdown = (peak - current) / peak
        
        return drawdown
    
    def check_drawdown_limit(self, current_portfolio_value):
        """Check if drawdown limit is exceeded"""
        self.portfolio_history.append(current_portfolio_value)
        
        # Keep only last 100 values
        if len(self.portfolio_history) > 100:
            self.portfolio_history = self.portfolio_history[-100:]
        
        drawdown = self.calculate_drawdown(self.portfolio_history)
        
        if drawdown > self.max_drawdown:
            logger.warning(f"Maximum drawdown exceeded: {drawdown:.2%}")
            return True, drawdown
        
        return False, drawdown
    
    def calculate_volatility_adjusted_size(self, base_size, volatility, symbol):
        """Adjust position size based on volatility"""
        try:
            # Normalize volatility (0-1 scale)
            normalized_vol = min(volatility * 100, 1.0)
            
            # Reduce size for high volatility
            volatility_multiplier = 1 - (normalized_vol * 0.5)
            
            # Ensure minimum size
            volatility_multiplier = max(volatility_multiplier, 0.3)
            
            adjusted_size = base_size * volatility_multiplier
            
            logger.info(f"{symbol} volatility adjustment: {volatility_multiplier:.2f}x")
            
            return adjusted_size
            
        except Exception as e:
            logger.error(f"Error calculating volatility adjusted size: {e}")
            return base_size
    
    def check_market_conditions(self, analysis_results):
        """Check overall market conditions for risk"""
        try:
            risk_factors = []
            
            # Check for high volatility across assets
            high_vol_count = sum(1 for analysis in analysis_results if analysis and analysis.get('high_volatility', False))
            if high_vol_count >= 2:
                risk_factors.append(f"High volatility in {high_vol_count} assets")
            
            # Check for extreme RSI values
            extreme_rsi_count = 0
            for analysis in analysis_results:
                if analysis:
                    rsi = analysis.get('rsi', 50)
                    if rsi < 20 or rsi > 80:
                        extreme_rsi_count += 1
            
            if extreme_rsi_count >= 2:
                risk_factors.append(f"Extreme RSI in {extreme_rsi_count} assets")
            
            # Check for volume anomalies
            volume_surge_count = sum(1 for analysis in analysis_results if analysis and analysis.get('volume_surge', False))
            if volume_surge_count >= 2:
                risk_factors.append(f"Volume surge in {volume_surge_count} assets")
            
            # Check for Bollinger Band squeezes
            bb_squeeze_count = sum(1 for analysis in analysis_results if analysis and analysis.get('bb_squeeze', False))
            if bb_squeeze_count >= 2:
                risk_factors.append(f"BB squeeze in {bb_squeeze_count} assets")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error checking market conditions: {e}")
            return []
    
    def validate_trade_risk(self, symbol, side, amount, current_portfolio_value, analysis):
        """Validate if a trade meets risk management criteria"""
        try:
            risk_checks = {
                'passed': True,
                'warnings': [],
                'adjusted_amount': amount
            }
            
            # Check portfolio concentration
            if current_portfolio_value > 0:
                concentration = amount / current_portfolio_value
                if concentration > Config.MAX_POSITION_SIZE:
                    risk_checks['warnings'].append(f"Position size exceeds {Config.MAX_POSITION_SIZE*100}% of portfolio")
                    risk_checks['adjusted_amount'] = current_portfolio_value * Config.MAX_POSITION_SIZE
            
            # Check drawdown limit
            drawdown_exceeded, drawdown = self.check_drawdown_limit(current_portfolio_value)
            if drawdown_exceeded:
                risk_checks['warnings'].append(f"Drawdown limit exceeded: {drawdown:.2%}")
                risk_checks['passed'] = False
            
            # Check volatility
            if analysis and analysis.get('high_volatility', False):
                risk_checks['warnings'].append("High volatility detected")
                risk_checks['adjusted_amount'] = self.calculate_volatility_adjusted_size(
                    risk_checks['adjusted_amount'], 
                    analysis.get('volatility', 0), 
                    symbol
                )
            
            # Check signal strength
            if analysis and analysis.get('signal_strength', 0) < 5:
                risk_checks['warnings'].append("Weak trading signal")
                risk_checks['adjusted_amount'] *= 0.5
            
            # Check ML confidence
            if analysis and analysis.get('ml_predictions'):
                confidence = analysis['ml_predictions'].get('combined_probability', 0.5)
                if confidence < 0.6:
                    risk_checks['warnings'].append("Low ML confidence")
                    risk_checks['adjusted_amount'] *= 0.7
            
            # Log risk assessment
            if risk_checks['warnings']:
                logger.warning(f"Risk warnings for {symbol} {side}: {', '.join(risk_checks['warnings'])}")
            
            return risk_checks
            
        except Exception as e:
            logger.error(f"Error validating trade risk: {e}")
            return {'passed': False, 'warnings': ['Risk validation error'], 'adjusted_amount': 0}
    
    def update_position_history(self, symbol, side, amount, price, timestamp):
        """Update position history for risk tracking"""
        position_record = {
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'timestamp': timestamp
        }
        
        self.position_history.append(position_record)
        
        # Keep only last 100 positions
        if len(self.position_history) > 100:
            self.position_history = self.position_history[-100:]
    
    def get_risk_metrics(self):
        """Get current risk metrics"""
        try:
            metrics = {
                'total_positions': len(self.position_history),
                'recent_positions': len([p for p in self.position_history 
                                       if p['timestamp'] > datetime.now() - timedelta(hours=24)]),
                'current_drawdown': 0,
                'avg_position_size': 0,
                'risk_score': 0
            }
            
            # Calculate current drawdown
            if self.portfolio_history:
                metrics['current_drawdown'] = self.calculate_drawdown(self.portfolio_history)
            
            # Calculate average position size
            if self.position_history:
                metrics['avg_position_size'] = np.mean([p['amount'] for p in self.position_history])
            
            # Calculate risk score (0-100, higher = more risky)
            risk_score = 0
            
            # Drawdown contribution
            risk_score += metrics['current_drawdown'] * 50
            
            # Position frequency contribution
            if metrics['recent_positions'] > 10:
                risk_score += 20
            
            # Position size contribution
            if metrics['avg_position_size'] > Config.TRADE_AMOUNT * 2:
                risk_score += 20
            
            metrics['risk_score'] = min(risk_score, 100)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def should_pause_trading(self, risk_metrics):
        """Determine if trading should be paused due to risk"""
        try:
            pause_reasons = []
            
            # Check drawdown
            if risk_metrics.get('current_drawdown', 0) > self.max_drawdown * 0.8:
                pause_reasons.append("Approaching drawdown limit")
            
            # Check risk score
            if risk_metrics.get('risk_score', 0) > 80:
                pause_reasons.append("High risk score")
            
            # Check recent trading frequency
            if risk_metrics.get('recent_positions', 0) > 15:
                pause_reasons.append("High trading frequency")
            
            if pause_reasons:
                logger.warning(f"Trading pause recommended: {', '.join(pause_reasons)}")
                return True, pause_reasons
            
            return False, []
            
        except Exception as e:
            logger.error(f"Error checking trading pause: {e}")
            return False, []
