"""
TradeX V3 - Main Application
Automated BTC Trading Platform
Entry point for the complete trading system
"""

import os
import sys
import logging
import time
import threading
from datetime import datetime
import signal

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_retriever import DataRetriever
from ml_predictor import MLPredictor
from risk_module import RiskModule
from logic_engine import LogicEngine
from executor import Executor
from trade_logger import TradeLogger
from terminal_interface import TerminalInterface

class TradingSystem:
    """Main trading system that orchestrates all modules"""
    
    def __init__(self):
        """Initialize the complete trading system"""
        self.config = Config()
        self.logger = self._setup_logging()
        
        self.logger.info("Initializing TradeX V3 Trading System...")
        
        # Initialize all modules
        try:
            self.data_retriever = DataRetriever()
            self.ml_predictor = MLPredictor()
            self.risk_module = RiskModule()
            self.logic_engine = LogicEngine()
            self.executor = Executor()
            self.trade_logger = TradeLogger()
            
            # Initialize terminal interface
            self.terminal_interface = TerminalInterface(self)
            
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize trading system: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/tradex_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            self.logger.info("Starting trading cycle...")
            
            # 1. Get market data
            market_data = self.data_retriever.get_market_data()
            if not market_data:
                self.logger.warning("Failed to get market data, skipping cycle")
                return False
            
            # 2. Get technical indicators
            indicators = self.data_retriever.get_latest_indicators()
            
            # 3. Get ML prediction
            ml_prediction = self.ml_predictor.predict(market_data['dataframe'])
            
            # 4. Analyze market conditions
            technical_analysis = self.logic_engine.analyze_technical_indicators(indicators)
            trend_analysis = self.logic_engine.analyze_trend_confirmation(market_data)
            liquidity_analysis = self.logic_engine.analyze_liquidity_volatility(market_data)
            
            # 5. Make trading decision
            decision = self.logic_engine.make_decision(
                technical_analysis, ml_prediction, trend_analysis, liquidity_analysis, market_data
            )
            
            # 6. Check risk management
            if decision and decision['decision'] != 'HOLD':
                risk_check = self.risk_module.check_risk_limits(decision)
                if not risk_check['allowed']:
                    self.logger.warning(f"Risk check failed: {risk_check['reason']}")
                    decision = {'decision': 'HOLD', 'confidence': 0.0, 'reason': 'Risk limits exceeded'}
            
            # 7. Execute trade if decision is made
            if decision and decision['decision'] != 'HOLD':
                trade_result = self.executor.execute_trade(decision, market_data)
                if trade_result:
                    self.logger.info(f"Trade executed: {trade_result}")
                else:
                    self.logger.warning("Trade execution failed")
            
            # 8. Log decision
            self.trade_logger.log_decision(decision, market_data['current_price'])
            
            self.logger.info("Trading cycle completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
            return False
    
    def run_automated_trading(self):
        """Run automated trading in a loop"""
        self.logger.info("Starting automated trading...")
        
        while True:
            try:
                # Run trading cycle
                success = self.run_trading_cycle()
                
                if not success:
                    self.logger.warning("Trading cycle failed, waiting before retry...")
                    time.sleep(self.config.UPDATE_INTERVAL * 2)
                else:
                    # Wait for next cycle
                    time.sleep(self.config.UPDATE_INTERVAL)
                    
            except KeyboardInterrupt:
                self.logger.info("Automated trading stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in automated trading: {e}")
                time.sleep(self.config.UPDATE_INTERVAL)
    
    def run_interactive_mode(self):
        """Run in interactive mode with terminal interface"""
        self.logger.info("Starting interactive mode...")
        
        try:
            # Show welcome message
            self.terminal_interface.print_header()
            self.terminal_interface.print_success("TradeX V3 - BTC Trading Platform")
            self.terminal_interface.print_info("Interactive mode started successfully")
            print()
            
            # Show main menu
            self.terminal_interface.show_main_menu()
            
        except KeyboardInterrupt:
            self.logger.info("Interactive mode stopped by user")
        except Exception as e:
            self.logger.error(f"Error in interactive mode: {e}")
    
    def run_backtest_mode(self, start_date, end_date):
        """Run backtest mode for historical analysis"""
        self.logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        try:
            # Get historical data
            historical_data = self.data_retriever.get_historical_data(start_date, end_date)
            
            if historical_data.empty:
                self.logger.error("No historical data available for backtest")
                return
            
            # Run backtest
            results = self._run_backtest(historical_data)
            
            # Display results
            self._display_backtest_results(results)
            
        except Exception as e:
            self.logger.error(f"Error in backtest mode: {e}")
    
    def _run_backtest(self, historical_data):
        """Run backtest on historical data"""
        results = {
            'trades': [],
            'initial_balance': 10000,  # $10,000 starting balance
            'current_balance': 10000,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        position = None
        
        for i in range(len(historical_data) - 1):
            try:
                # Get data up to current point
                current_data = historical_data.iloc[:i+1]
                current_price = current_data.iloc[-1]['close']
                
                # Get indicators for current data
                indicators = self.data_retriever.calculate_indicators(current_data)
                if not indicators:
                    continue
                
                # Get ML prediction
                ml_prediction = self.ml_predictor.predict(current_data)
                
                # Analyze market conditions
                technical_analysis = self.logic_engine.analyze_technical_indicators(indicators.iloc[-1])
                trend_analysis = self.logic_engine.analyze_trend_confirmation({'dataframe': current_data})
                liquidity_analysis = self.logic_engine.analyze_liquidity_volatility({'dataframe': current_data})
                
                # Make decision
                decision = self.logic_engine.make_decision(
                    technical_analysis, ml_prediction, trend_analysis, liquidity_analysis
                )
                
                # Execute trades based on decision
                if decision and decision['decision'] != 'HOLD':
                    if decision['decision'] == 'BUY' and position is None:
                        # Open long position
                        position = {
                            'type': 'LONG',
                            'entry_price': current_price,
                            'entry_time': current_data.index[-1],
                            'quantity': results['current_balance'] * 0.95 / current_price  # Use 95% of balance
                        }
                        results['total_trades'] += 1
                        
                    elif decision['decision'] == 'SELL' and position is not None:
                        # Close position
                        exit_price = current_price
                        pnl = (exit_price - position['entry_price']) * position['quantity']
                        results['current_balance'] += pnl
                        
                        trade_result = {
                            'entry_time': position['entry_time'],
                            'exit_time': current_data.index[-1],
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'quantity': position['quantity'],
                            'pnl': pnl,
                            'return_pct': (pnl / (position['entry_price'] * position['quantity'])) * 100
                        }
                        
                        results['trades'].append(trade_result)
                        
                        if pnl > 0:
                            results['winning_trades'] += 1
                        else:
                            results['losing_trades'] += 1
                        
                        position = None
                
            except Exception as e:
                self.logger.error(f"Error in backtest iteration {i}: {e}")
                continue
        
        # Close any open position at the end
        if position is not None:
            final_price = historical_data.iloc[-1]['close']
            pnl = (final_price - position['entry_price']) * position['quantity']
            results['current_balance'] += pnl
            
            trade_result = {
                'entry_time': position['entry_time'],
                'exit_time': historical_data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'quantity': position['quantity'],
                'pnl': pnl,
                'return_pct': (pnl / (position['entry_price'] * position['quantity'])) * 100
            }
            
            results['trades'].append(trade_result)
            
            if pnl > 0:
                results['winning_trades'] += 1
            else:
                results['losing_trades'] += 1
        
        return results
    
    def _display_backtest_results(self, results):
        """Display backtest results"""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        
        total_return = ((results['current_balance'] - results['initial_balance']) / results['initial_balance']) * 100
        
        print(f"Initial Balance: ${results['initial_balance']:,.2f}")
        print(f"Final Balance: ${results['current_balance']:,.2f}")
        print(f"Total Return: {total_return:+.2f}%")
        print()
        
        print(f"Total Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        
        if results['total_trades'] > 0:
            win_rate = (results['winning_trades'] / results['total_trades']) * 100
            print(f"Win Rate: {win_rate:.2f}%")
        
        if results['trades']:
            avg_win = sum(t['pnl'] for t in results['trades'] if t['pnl'] > 0) / max(1, results['winning_trades'])
            avg_loss = sum(t['pnl'] for t in results['trades'] if t['pnl'] < 0) / max(1, results['losing_trades'])
            print(f"Average Win: ${avg_win:,.2f}")
            print(f"Average Loss: ${avg_loss:,.2f}")
        
        print("="*60)
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up trading system...")
        
        try:
            # Stop any running threads
            if hasattr(self, 'terminal_interface') and self.terminal_interface.monitoring:
                self.terminal_interface.stop_monitoring()
            
            # Cleanup old data
            if hasattr(self, 'trade_logger'):
                self.trade_logger.cleanup_old_data()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    print("\nReceived signal to shutdown. Cleaning up...")
    if hasattr(signal_handler, 'trading_system'):
        signal_handler.trading_system.cleanup()
    sys.exit(0)

def main():
    """Main entry point"""
    print("TradeX V3 - BTC Trading Platform")
    print("="*50)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize trading system
        trading_system = TradingSystem()
        signal_handler.trading_system = trading_system
        
        # Parse command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == 'auto':
                # Automated trading mode
                trading_system.run_automated_trading()
            elif mode == 'backtest':
                # Backtest mode
                if len(sys.argv) >= 4:
                    start_date = sys.argv[2]
                    end_date = sys.argv[3]
                    trading_system.run_backtest_mode(start_date, end_date)
                else:
                    print("Usage: python main.py backtest <start_date> <end_date>")
                    print("Example: python main.py backtest 2024-01-01 2024-01-31")
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: auto, backtest, interactive (default)")
                return
        else:
            # Interactive mode (default)
            trading_system.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        if 'trading_system' in locals():
            trading_system.cleanup()

if __name__ == "__main__":
    main()
