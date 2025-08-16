"""
TradeX V3 - Logic Engine Module
Central decision hub that weighs technical indicators, ML predictions, and risk assessment
"""

import logging
import numpy as np
from datetime import datetime
from config import Config

class LogicEngine:
    def __init__(self):
        """Initialize Logic Engine"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Decision weights
        self.technical_weight = self.config.TECHNICAL_INDICATORS_WEIGHT
        self.ml_weight = self.config.ML_PREDICTION_WEIGHT
        self.trend_weight = self.config.TREND_CONFIRMATION_WEIGHT
        self.liquidity_weight = self.config.LIQUIDITY_VOLATILITY_WEIGHT
        
        self.logger.info("Logic Engine initialized")
    
    def analyze_technical_indicators(self, indicators):
        """Analyze technical indicators and return signal"""
        try:
            if not indicators:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'No indicators available'}
            
            signals = []
            confidences = []
            
            # RSI Analysis
            rsi = indicators.get('rsi')
            if rsi is not None:
                if rsi < 30:
                    signals.append('BUY')
                    confidences.append(0.8)
                elif rsi > 70:
                    signals.append('SELL')
                    confidences.append(0.8)
                else:
                    signals.append('HOLD')
                    confidences.append(0.5)
            
            # MACD Analysis
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            if macd is not None and macd_signal is not None:
                if macd > macd_signal:
                    signals.append('BUY')
                    confidences.append(0.7)
                else:
                    signals.append('SELL')
                    confidences.append(0.7)
            
            # Bollinger Bands Analysis
            bb_position = indicators.get('bb_position')
            if bb_position is not None:
                if bb_position < 0.2:
                    signals.append('BUY')
                    confidences.append(0.6)
                elif bb_position > 0.8:
                    signals.append('SELL')
                    confidences.append(0.6)
                else:
                    signals.append('HOLD')
                    confidences.append(0.5)
            
            # Moving Averages Analysis
            current_price = indicators.get('current_price')
            if current_price:
                sma_signals = []
                for period in self.config.SMA_PERIODS:
                    sma_key = f'sma_{period}'
                    sma_value = indicators.get(sma_key)
                    if sma_value and current_price > sma_value:
                        sma_signals.append('BUY')
                    elif sma_value and current_price < sma_value:
                        sma_signals.append('SELL')
                
                if sma_signals:
                    # Majority vote for moving averages
                    buy_count = sma_signals.count('BUY')
                    sell_count = sma_signals.count('SELL')
                    if buy_count > sell_count:
                        signals.append('BUY')
                        confidences.append(0.6)
                    elif sell_count > buy_count:
                        signals.append('SELL')
                        confidences.append(0.6)
                    else:
                        signals.append('HOLD')
                        confidences.append(0.5)
            
            # Calculate weighted signal
            if signals:
                signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
                signal_confidences = {'BUY': [], 'SELL': [], 'HOLD': []}
                
                for signal, confidence in zip(signals, confidences):
                    signal_counts[signal] += 1
                    signal_confidences[signal].append(confidence)
                
                # Find dominant signal
                dominant_signal = max(signal_counts, key=signal_counts.get)
                avg_confidence = np.mean(signal_confidences[dominant_signal]) if signal_confidences[dominant_signal] else 0.5
                
                return {
                    'signal': dominant_signal,
                    'confidence': avg_confidence,
                    'reason': f'Technical analysis: {dominant_signal} signal from {signal_counts[dominant_signal]} indicators'
                }
            else:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'No technical signals'}
                
        except Exception as e:
            self.logger.error(f"Error analyzing technical indicators: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'reason': f'Error: {e}'}
    
    def analyze_trend_confirmation(self, market_data):
        """Analyze trend confirmation"""
        try:
            if not market_data or 'dataframe' not in market_data:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'No market data available'}
            
            df = market_data['dataframe']
            if df.empty:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'Empty market data'}
            
            # Get recent price trends
            recent_prices = df['close'].tail(6)  # Last 6 hours
            if len(recent_prices) < 3:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'Insufficient price data'}
            
            # Calculate trend
            price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # Determine trend signal
            if price_change > 0.02:  # 2% uptrend
                signal = 'BUY'
                confidence = min(0.8, 0.5 + abs(price_change) * 10)
            elif price_change < -0.02:  # 2% downtrend
                signal = 'SELL'
                confidence = min(0.8, 0.5 + abs(price_change) * 10)
            else:
                signal = 'HOLD'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': confidence,
                'reason': f'Trend analysis: {price_change:.2%} price change over 6 hours'
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'reason': f'Error: {e}'}
    
    def analyze_liquidity_volatility(self, market_data):
        """Analyze liquidity and volatility"""
        try:
            if not market_data or 'stats_24h' not in market_data:
                return {'signal': 'HOLD', 'confidence': 0.5, 'reason': 'No 24h stats available'}
            
            stats = market_data['stats_24h']
            
            # Analyze volume
            volume = stats.get('volume', 0)
            quote_volume = stats.get('quote_volume', 0)
            
            # Analyze price volatility
            high_24h = stats.get('high_24h', 0)
            low_24h = stats.get('low_24h', 0)
            current_price = market_data.get('current_price', 0)
            
            if current_price > 0:
                volatility = (high_24h - low_24h) / current_price
            else:
                volatility = 0
            
            # Determine signal based on liquidity and volatility
            if volume > 1000 and quote_volume > 1000000:  # Good liquidity
                if volatility < 0.05:  # Low volatility
                    signal = 'BUY'
                    confidence = 0.7
                    reason = 'Good liquidity, low volatility'
                elif volatility > 0.1:  # High volatility
                    signal = 'HOLD'
                    confidence = 0.6
                    reason = 'Good liquidity, high volatility - cautious'
                else:
                    signal = 'HOLD'
                    confidence = 0.5
                    reason = 'Good liquidity, moderate volatility'
            else:
                signal = 'HOLD'
                confidence = 0.4
                reason = 'Low liquidity - trading not recommended'
            
            return {
                'signal': signal,
                'confidence': confidence,
                'reason': reason
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing liquidity/volatility: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'reason': f'Error: {e}'}
    
    def make_decision(self, technical_analysis, ml_prediction, trend_analysis, liquidity_analysis, market_data=None):
        """Make weighted decision based on all inputs with market regime detection"""
        try:
            # Detect market regime
            market_regime = self._detect_market_regime(market_data) if market_data else 'UNKNOWN'
            
            # Adjust weights based on market regime
            adjusted_weights = self._adjust_weights_for_regime(market_regime)
            
            # Collect all signals and confidences
            signals = []
            confidences = []
            weights = []
            reasons = []
            
            # Technical indicators
            if technical_analysis:
                signals.append(technical_analysis['signal'])
                confidences.append(technical_analysis['confidence'])
                weights.append(adjusted_weights['technical'])
                reasons.append(technical_analysis['reason'])
            
            # ML prediction
            if ml_prediction:
                signals.append(ml_prediction['signal'])
                confidences.append(ml_prediction['confidence'])
                weights.append(adjusted_weights['ml'])
                reasons.append(f"ML prediction: {ml_prediction['signal']}")
            
            # Trend confirmation
            if trend_analysis:
                signals.append(trend_analysis['signal'])
                confidences.append(trend_analysis['confidence'])
                weights.append(adjusted_weights['trend'])
                reasons.append(trend_analysis['reason'])
            
            # Liquidity and volatility
            if liquidity_analysis:
                signals.append(liquidity_analysis['signal'])
                confidences.append(liquidity_analysis['confidence'])
                weights.append(adjusted_weights['liquidity'])
                reasons.append(liquidity_analysis['reason'])
            
            if not signals:
                return {
                    'decision': 'HOLD',
                    'confidence': 0.5,
                    'reason': 'No analysis data available',
                    'timestamp': datetime.now(),
                    'market_regime': market_regime
                }
            
            # Calculate weighted decision
            signal_scores = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            total_weight = sum(weights)
            
            for signal, confidence, weight in zip(signals, confidences, weights):
                normalized_weight = weight / total_weight
                signal_scores[signal] += confidence * normalized_weight
            
            # Determine final decision
            final_signal = max(signal_scores, key=signal_scores.get)
            final_confidence = signal_scores[final_signal]
            
            # Apply regime-specific confidence adjustments
            final_confidence = self._adjust_confidence_for_regime(final_confidence, market_regime)
            
            # Combine reasons
            combined_reason = ' | '.join(reasons) + f' | Regime: {market_regime}'
            
            decision = {
                'decision': final_signal,
                'confidence': final_confidence,
                'reason': combined_reason,
                'timestamp': datetime.now(),
                'market_regime': market_regime,
                'signal_breakdown': {
                    'technical': technical_analysis,
                    'ml': ml_prediction,
                    'trend': trend_analysis,
                    'liquidity': liquidity_analysis
                }
            }
            
            self.logger.info(f"Decision: {final_signal} (confidence: {final_confidence:.4f}, regime: {market_regime})")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            return {
                'decision': 'HOLD',
                'confidence': 0.5,
                'reason': f'Error in decision making: {e}',
                'timestamp': datetime.now(),
                'market_regime': 'UNKNOWN'
            }
    
    def _detect_market_regime(self, market_data):
        """Detect current market regime (trending/ranging/volatile)"""
        try:
            if not market_data or 'dataframe' not in market_data:
                return 'UNKNOWN'
            
            df = market_data['dataframe']
            if df.empty:
                return 'UNKNOWN'
            
            # Calculate volatility
            returns = df['close'].pct_change().dropna()
            volatility = returns.std()
            
            # Calculate trend strength using ADX
            adx = df.get('adx', None)
            if adx is not None and not adx.isna().all():
                trend_strength = adx.iloc[-1]
            else:
                # Simple trend calculation
                sma_20 = df['close'].rolling(20).mean()
                sma_50 = df['close'].rolling(50).mean()
                trend_strength = abs(sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100
            
            # Determine regime
            if volatility > 0.03:  # High volatility
                if trend_strength > 25:
                    return 'BULLISH_HIGH' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'BEARISH_HIGH'
                else:
                    return 'SIDEWAYS_HIGH'
            elif volatility > 0.015:  # Medium volatility
                if trend_strength > 25:
                    return 'BULLISH_MEDIUM' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'BEARISH_MEDIUM'
                else:
                    return 'SIDEWAYS_MEDIUM'
            else:  # Low volatility
                if trend_strength > 25:
                    return 'BULLISH_LOW' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'BEARISH_LOW'
                else:
                    return 'SIDEWAYS_LOW'
                    
        except Exception as e:
            self.logger.error(f"Error detecting market regime: {e}")
            return 'UNKNOWN'
    
    def _adjust_weights_for_regime(self, regime):
        """Adjust analysis weights based on market regime"""
        try:
            base_weights = {
                'technical': self.technical_weight,
                'ml': self.ml_weight,
                'trend': self.trend_weight,
                'liquidity': self.liquidity_weight
            }
            
            if not hasattr(self.config, 'REGIME_ADAPTATION') or not self.config.REGIME_ADAPTATION:
                return base_weights
            
            # Regime-specific weight adjustments
            if 'BULLISH' in regime:
                # In bullish markets, favor trend and ML predictions
                base_weights['trend'] *= 1.2
                base_weights['ml'] *= 1.1
                base_weights['technical'] *= 0.9
            elif 'BEARISH' in regime:
                # In bearish markets, favor technical indicators and liquidity
                base_weights['technical'] *= 1.2
                base_weights['liquidity'] *= 1.1
                base_weights['ml'] *= 0.9
            elif 'SIDEWAYS' in regime:
                # In sideways markets, favor technical indicators
                base_weights['technical'] *= 1.3
                base_weights['trend'] *= 0.8
            
            # Normalize weights
            total = sum(base_weights.values())
            normalized_weights = {k: v/total for k, v in base_weights.items()}
            
            return normalized_weights
            
        except Exception as e:
            self.logger.error(f"Error adjusting weights for regime: {e}")
            return {
                'technical': self.technical_weight,
                'ml': self.ml_weight,
                'trend': self.trend_weight,
                'liquidity': self.liquidity_weight
            }
    
    def _adjust_confidence_for_regime(self, confidence, regime):
        """Adjust confidence based on market regime"""
        try:
            if not hasattr(self.config, 'REGIME_ADAPTATION') or not self.config.REGIME_ADAPTATION:
                return confidence
            
            # Regime-specific confidence adjustments
            if 'HIGH' in regime:
                # Reduce confidence in high volatility
                confidence *= 0.8
            elif 'LOW' in regime:
                # Increase confidence in low volatility
                confidence *= 1.1
            
            return min(confidence, 1.0)  # Cap at 100%
            
        except Exception as e:
            self.logger.error(f"Error adjusting confidence for regime: {e}")
            return confidence
    
    def get_decision_summary(self, decision):
        """Get a summary of the decision"""
        try:
            if not decision:
                return "No decision available"
            
            summary = f"Decision: {decision['decision']}\n"
            summary += f"Confidence: {decision['confidence']:.2%}\n"
            summary += f"Reason: {decision['reason']}\n"
            summary += f"Time: {decision['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting decision summary: {e}")
            return "Error generating summary"
