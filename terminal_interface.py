"""
TradeX V3 - Terminal Interface Module
Beautiful terminal interface with menu for monitoring, testing, and viewing logs
"""

import os
import time
import threading
from datetime import datetime
import logging
from colorama import init, Fore, Back, Style
from tabulate import tabulate
import pandas as pd

# Initialize colorama for cross-platform colored output
init()

class TerminalInterface:
    def __init__(self, trading_system):
        """Initialize Terminal Interface"""
        self.trading_system = trading_system
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
        self.logger.info("Terminal Interface initialized")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print TradeX header"""
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}                    TradeX V3 - BTC Trading Platform")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print()
    
    def print_status(self, status_type, message, color=Fore.WHITE):
        """Print status message with color"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}[{timestamp}] {status_type}: {message}{Style.RESET_ALL}")
    
    def print_success(self, message):
        """Print success message"""
        self.print_status("SUCCESS", message, Fore.GREEN)
    
    def print_error(self, message):
        """Print error message"""
        self.print_status("ERROR", message, Fore.RED)
    
    def print_warning(self, message):
        """Print warning message"""
        self.print_status("WARNING", message, Fore.YELLOW)
    
    def print_info(self, message):
        """Print info message"""
        self.print_status("INFO", message, Fore.BLUE)
    
    def show_main_menu(self):
        """Show main menu"""
        while True:
            self.print_header()
            print(f"{Fore.WHITE}Main Menu:{Style.RESET_ALL}")
            print()
            print(f"{Fore.CYAN}1.{Style.RESET_ALL} Start Monitoring")
            print(f"{Fore.CYAN}2.{Style.RESET_ALL} Test Logic")
            print(f"{Fore.CYAN}3.{Style.RESET_ALL} View Logs & Analytics")
            print(f"{Fore.CYAN}4.{Style.RESET_ALL} System Status")
            print(f"{Fore.CYAN}5.{Style.RESET_ALL} Configuration")
            print(f"{Fore.CYAN}6.{Style.RESET_ALL} Exit")
            print()
            
            choice = input(f"{Fore.YELLOW}Select an option (1-6): {Style.RESET_ALL}")
            
            if choice == '1':
                self.start_monitoring()
            elif choice == '2':
                self.test_logic()
            elif choice == '3':
                self.view_logs_analytics()
            elif choice == '4':
                self.show_system_status()
            elif choice == '5':
                self.show_configuration()
            elif choice == '6':
                self.exit_system()
                break
            else:
                self.print_error("Invalid option. Please try again.")
                time.sleep(2)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring:
            self.print_warning("Monitoring is already running!")
            input("Press Enter to continue...")
            return
        
        self.print_header()
        print(f"{Fore.GREEN}Starting TradeX Monitoring...{Style.RESET_ALL}")
        print()
        
        # Start monitoring in a separate thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.print_success("Monitoring started successfully!")
        print()
        print(f"{Fore.YELLOW}Press Enter to stop monitoring...{Style.RESET_ALL}")
        input()
        
        self.stop_monitoring()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring:
                self.clear_screen()
                self.print_header()
                self.show_monitoring_dashboard()
                time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            self.monitoring = False
    
    def show_monitoring_dashboard(self):
        """Show real-time monitoring dashboard"""
        try:
            # Get current market data
            market_data = self.trading_system.data_retriever.get_market_data()
            if not market_data:
                self.print_error("Failed to get market data")
                return
            
            current_price = market_data.get('current_price', 0)
            stats_24h = market_data.get('stats_24h', {})
            
            # Get latest indicators
            indicators = self.trading_system.data_retriever.get_latest_indicators()
            
            # Get ML prediction
            ml_prediction = self.trading_system.ml_predictor.predict(market_data['dataframe'])
            
            # Get risk metrics
            risk_metrics = self.trading_system.risk_module.get_risk_metrics()
            
            # Get trading summary
            trading_summary = self.trading_system.executor.get_trading_summary()
            
            # Display dashboard
            print(f"{Fore.WHITE}Real-Time Monitoring Dashboard{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print()
            
            # Price and market info
            print(f"{Fore.YELLOW}Market Information:{Style.RESET_ALL}")
            print(f"Current BTC Price: {Fore.GREEN}${current_price:,.2f}{Style.RESET_ALL}")
            if stats_24h:
                change_24h = stats_24h.get('price_change_percent', 0)
                change_color = Fore.GREEN if change_24h >= 0 else Fore.RED
                print(f"24h Change: {change_color}{change_24h:+.2f}%{Style.RESET_ALL}")
                print(f"24h Volume: {stats_24h.get('volume', 0):,.0f} BTC")
            print()
            
            # Technical indicators
            if indicators:
                print(f"{Fore.YELLOW}Technical Indicators:{Style.RESET_ALL}")
                rsi = indicators.get('rsi', 0)
                rsi_color = Fore.RED if rsi > 70 else (Fore.GREEN if rsi < 30 else Fore.YELLOW)
                print(f"RSI: {rsi_color}{rsi:.2f}{Style.RESET_ALL}")
                
                macd = indicators.get('macd', 0)
                macd_signal = indicators.get('macd_signal', 0)
                macd_color = Fore.GREEN if macd > macd_signal else Fore.RED
                print(f"MACD: {macd_color}{macd:.4f}{Style.RESET_ALL} (Signal: {macd_signal:.4f})")
                
                bb_position = indicators.get('bb_position', 0)
                bb_color = Fore.RED if bb_position > 0.8 else (Fore.GREEN if bb_position < 0.2 else Fore.YELLOW)
                print(f"BB Position: {bb_color}{bb_position:.2f}{Style.RESET_ALL}")
            print()
            
            # ML prediction
            if ml_prediction:
                print(f"{Fore.YELLOW}ML Prediction:{Style.RESET_ALL}")
                signal = ml_prediction.get('signal', 'HOLD')
                confidence = ml_prediction.get('confidence', 0)
                signal_color = Fore.GREEN if signal == 'BUY' else (Fore.RED if signal == 'SELL' else Fore.YELLOW)
                print(f"Signal: {signal_color}{signal}{Style.RESET_ALL}")
                print(f"Confidence: {confidence:.2%}")
            print()
            
            # Risk metrics
            print(f"{Fore.YELLOW}Risk Metrics:{Style.RESET_ALL}")
            print(f"Daily Trades: {risk_metrics.get('daily_trades', 0)}/{risk_metrics.get('max_daily_trades', 0)}")
            print(f"Daily PnL: {risk_metrics.get('daily_pnl', 0):.2f}%")
            print(f"Active Positions: {risk_metrics.get('active_positions', 0)}")
            print()
            
            # Trading summary
            if trading_summary:
                print(f"{Fore.YELLOW}Trading Summary:{Style.RESET_ALL}")
                balance = trading_summary.get('balance', {})
                print(f"USDT Balance: ${balance.get('USDT', 0):,.2f}")
                print(f"BTC Balance: {balance.get('BTC', 0):.6f}")
                
                if trading_summary.get('paper_trading'):
                    pnl = trading_summary.get('paper_pnl', 0)
                    pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
                    print(f"Paper PnL: {pnl_color}${pnl:,.2f}{Style.RESET_ALL}")
            print()
            
            # Status
            status_color = Fore.GREEN if self.monitoring else Fore.RED
            print(f"Status: {status_color}{'MONITORING' if self.monitoring else 'STOPPED'}{Style.RESET_ALL}")
            print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error showing monitoring dashboard: {e}")
            self.print_error(f"Dashboard error: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.print_info("Monitoring stopped")
    
    def test_logic(self):
        """Test trading logic without executing trades"""
        self.print_header()
        print(f"{Fore.YELLOW}Testing Trading Logic...{Style.RESET_ALL}")
        print()
        
        try:
            # Get market data
            market_data = self.trading_system.data_retriever.get_market_data()
            if not market_data:
                self.print_error("Failed to get market data")
                input("Press Enter to continue...")
                return
            
            # Get technical indicators
            indicators = self.trading_system.data_retriever.get_latest_indicators()
            
            # Get ML prediction
            ml_prediction = self.trading_system.ml_predictor.predict(market_data['dataframe'])
            
            # Analyze components
            technical_analysis = self.trading_system.logic_engine.analyze_technical_indicators(indicators)
            trend_analysis = self.trading_system.logic_engine.analyze_trend_confirmation(market_data)
            liquidity_analysis = self.trading_system.logic_engine.analyze_liquidity_volatility(market_data)
            
            # Make decision
            decision = self.trading_system.logic_engine.make_decision(
                technical_analysis, ml_prediction, trend_analysis, liquidity_analysis
            )
            
            # Display results
            print(f"{Fore.WHITE}Logic Test Results:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print()
            
            # Technical analysis
            if technical_analysis:
                print(f"{Fore.YELLOW}Technical Analysis:{Style.RESET_ALL}")
                print(f"Signal: {technical_analysis['signal']}")
                print(f"Confidence: {technical_analysis['confidence']:.2%}")
                print(f"Reason: {technical_analysis['reason']}")
            print()
            
            # ML prediction
            if ml_prediction:
                print(f"{Fore.YELLOW}ML Prediction:{Style.RESET_ALL}")
                print(f"Signal: {ml_prediction['signal']}")
                print(f"Confidence: {ml_prediction['confidence']:.2%}")
            print()
            
            # Trend analysis
            if trend_analysis:
                print(f"{Fore.YELLOW}Trend Analysis:{Style.RESET_ALL}")
                print(f"Signal: {trend_analysis['signal']}")
                print(f"Confidence: {trend_analysis['confidence']:.2%}")
                print(f"Reason: {trend_analysis['reason']}")
            print()
            
            # Liquidity analysis
            if liquidity_analysis:
                print(f"{Fore.YELLOW}Liquidity Analysis:{Style.RESET_ALL}")
                print(f"Signal: {liquidity_analysis['signal']}")
                print(f"Confidence: {liquidity_analysis['confidence']:.2%}")
                print(f"Reason: {liquidity_analysis['reason']}")
            print()
            
            # Final decision
            if decision:
                print(f"{Fore.WHITE}Final Decision:{Style.RESET_ALL}")
                decision_color = Fore.GREEN if decision['decision'] == 'BUY' else (Fore.RED if decision['decision'] == 'SELL' else Fore.YELLOW)
                print(f"Decision: {decision_color}{decision['decision']}{Style.RESET_ALL}")
                print(f"Confidence: {decision['confidence']:.2%}")
                print(f"Reason: {decision['reason']}")
            
            self.print_success("Logic test completed successfully!")
            
        except Exception as e:
            self.logger.error(f"Error testing logic: {e}")
            self.print_error(f"Logic test failed: {e}")
        
        input("Press Enter to continue...")
    
    def view_logs_analytics(self):
        """View logs and analytics"""
        while True:
            self.print_header()
            print(f"{Fore.WHITE}Logs & Analytics Menu:{Style.RESET_ALL}")
            print()
            print(f"{Fore.CYAN}1.{Style.RESET_ALL} View Recent Trades")
            print(f"{Fore.CYAN}2.{Style.RESET_ALL} Performance Metrics")
            print(f"{Fore.CYAN}3.{Style.RESET_ALL} Recent Decisions")
            print(f"{Fore.CYAN}4.{Style.RESET_ALL} Export Data")
            print(f"{Fore.CYAN}5.{Style.RESET_ALL} Back to Main Menu")
            print()
            
            choice = input(f"{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}")
            
            if choice == '1':
                self.view_recent_trades()
            elif choice == '2':
                self.view_performance_metrics()
            elif choice == '3':
                self.view_recent_decisions()
            elif choice == '4':
                self.export_data()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid option. Please try again.")
                time.sleep(2)
    
    def view_recent_trades(self):
        """View recent trades"""
        self.print_header()
        print(f"{Fore.YELLOW}Recent Trades:{Style.RESET_ALL}")
        print()
        
        try:
            # Get recent trades
            trades_df = self.trading_system.trade_logger.get_trade_history(days=7)
            
            if trades_df.empty:
                print("No trades found in the last 7 days.")
            else:
                # Display trades in a table
                display_trades = trades_df[['order_id', 'side', 'quantity', 'entry_price', 'pnl', 'status', 'created_at']].head(20)
                
                # Format the data
                display_trades['entry_price'] = display_trades['entry_price'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
                display_trades['pnl'] = display_trades['pnl'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
                display_trades['created_at'] = display_trades['created_at'].apply(lambda x: str(x)[:19] if pd.notna(x) else "N/A")
                
                print(tabulate(display_trades, headers='keys', tablefmt='grid'))
            
        except Exception as e:
            self.logger.error(f"Error viewing recent trades: {e}")
            self.print_error(f"Failed to load trades: {e}")
        
        input("Press Enter to continue...")
    
    def view_performance_metrics(self):
        """View performance metrics"""
        self.print_header()
        print(f"{Fore.YELLOW}Performance Metrics (Last 30 Days):{Style.RESET_ALL}")
        print()
        
        try:
            metrics = self.trading_system.trade_logger.calculate_performance_metrics(days=30)
            
            if not metrics:
                print("No performance data available.")
            else:
                print(f"{Fore.WHITE}Performance Summary:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
                print(f"Total Trades: {metrics['total_trades']}")
                print(f"Winning Trades: {metrics['winning_trades']}")
                print(f"Losing Trades: {metrics['losing_trades']}")
                print(f"Win Rate: {metrics['win_rate']:.2f}%")
                print()
                
                print(f"{Fore.WHITE}Financial Metrics:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
                total_pnl = metrics['total_pnl']
                pnl_color = Fore.GREEN if total_pnl >= 0 else Fore.RED
                print(f"Total PnL: {pnl_color}${total_pnl:,.2f}{Style.RESET_ALL}")
                print(f"Average Win: ${metrics['avg_win']:,.2f}")
                print(f"Average Loss: ${metrics['avg_loss']:,.2f}")
                print(f"Profit Factor: {metrics['profit_factor']:.2f}")
                print()
                
                print(f"{Fore.WHITE}Risk Metrics:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
                print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
                print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error viewing performance metrics: {e}")
            self.print_error(f"Failed to load metrics: {e}")
        
        input("Press Enter to continue...")
    
    def view_recent_decisions(self):
        """View recent decisions"""
        self.print_header()
        print(f"{Fore.YELLOW}Recent Decisions:{Style.RESET_ALL}")
        print()
        
        try:
            decisions_df = self.trading_system.trade_logger.get_recent_decisions(limit=20)
            
            if decisions_df.empty:
                print("No recent decisions found.")
            else:
                # Display decisions in a table
                display_decisions = decisions_df[['timestamp', 'decision', 'confidence', 'current_price']].head(20)
                
                # Format the data
                display_decisions['confidence'] = display_decisions['confidence'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
                display_decisions['current_price'] = display_decisions['current_price'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
                display_decisions['timestamp'] = display_decisions['timestamp'].apply(lambda x: str(x)[:19] if pd.notna(x) else "N/A")
                
                print(tabulate(display_decisions, headers='keys', tablefmt='grid'))
            
        except Exception as e:
            self.logger.error(f"Error viewing recent decisions: {e}")
            self.print_error(f"Failed to load decisions: {e}")
        
        input("Press Enter to continue...")
    
    def export_data(self):
        """Export trading data"""
        self.print_header()
        print(f"{Fore.YELLOW}Export Data:{Style.RESET_ALL}")
        print()
        
        try:
            filename = self.trading_system.trade_logger.export_trades_to_csv()
            if filename:
                self.print_success(f"Data exported successfully to: {filename}")
            else:
                self.print_error("Failed to export data")
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            self.print_error(f"Export failed: {e}")
        
        input("Press Enter to continue...")
    
    def show_system_status(self):
        """Show system status"""
        self.print_header()
        print(f"{Fore.YELLOW}System Status:{Style.RESET_ALL}")
        print()
        
        try:
            # Check each component
            components = [
                ("Data Retriever", self.trading_system.data_retriever),
                ("ML Predictor", self.trading_system.ml_predictor),
                ("Risk Module", self.trading_system.risk_module),
                ("Logic Engine", self.trading_system.logic_engine),
                ("Executor", self.trading_system.executor),
                ("Trade Logger", self.trading_system.trade_logger)
            ]
            
            for name, component in components:
                status = "OK" if component else "ERROR"
                color = Fore.GREEN if status == "OK" else Fore.RED
                print(f"{name}: {color}{status}{Style.RESET_ALL}")
            
            print()
            
            # Get trading summary
            trading_summary = self.trading_system.executor.get_trading_summary()
            if trading_summary:
                print(f"{Fore.WHITE}Trading Status:{Style.RESET_ALL}")
                print(f"Paper Trading: {'Yes' if trading_summary.get('paper_trading') else 'No'}")
                print(f"Current Price: ${trading_summary.get('current_price', 0):,.2f}")
                
                if trading_summary.get('paper_trading'):
                    balance = trading_summary.get('balance', {})
                    print(f"USDT Balance: ${balance.get('USDT', 0):,.2f}")
                    print(f"BTC Balance: {balance.get('BTC', 0):.6f}")
            
        except Exception as e:
            self.logger.error(f"Error showing system status: {e}")
            self.print_error(f"Failed to get system status: {e}")
        
        input("Press Enter to continue...")
    
    def show_configuration(self):
        """Show current configuration"""
        self.print_header()
        print(f"{Fore.YELLOW}Current Configuration:{Style.RESET_ALL}")
        print()
        
        try:
            config = self.trading_system.config
            
            print(f"{Fore.WHITE}Trading Settings:{Style.RESET_ALL}")
            print(f"Symbol: {config.SYMBOL}")
            print(f"Paper Trading: {config.PAPER_TRADING}")
            print(f"Update Interval: {config.UPDATE_INTERVAL} seconds")
            print()
            
            print(f"{Fore.WHITE}Risk Management:{Style.RESET_ALL}")
            print(f"Stop Loss: {config.STOP_LOSS_PERCENTAGE}%")
            print(f"Take Profit: {config.TAKE_PROFIT_PERCENTAGE}%")
            print(f"Max Daily Trades: {config.MAX_DAILY_TRADES}")
            print(f"Max Daily Loss: {config.MAX_DAILY_LOSS}%")
            print()
            
            print(f"{Fore.WHITE}Logic Engine Weights:{Style.RESET_ALL}")
            print(f"Technical Indicators: {config.TECHNICAL_INDICATORS_WEIGHT:.1%}")
            print(f"ML Prediction: {config.ML_PREDICTION_WEIGHT:.1%}")
            print(f"Trend Confirmation: {config.TREND_CONFIRMATION_WEIGHT:.1%}")
            print(f"Liquidity & Volatility: {config.LIQUIDITY_VOLATILITY_WEIGHT:.1%}")
            
        except Exception as e:
            self.logger.error(f"Error showing configuration: {e}")
            self.print_error(f"Failed to get configuration: {e}")
        
        input("Press Enter to continue...")
    
    def exit_system(self):
        """Exit the system"""
        self.print_header()
        print(f"{Fore.YELLOW}Exiting TradeX...{Style.RESET_ALL}")
        
        # Stop monitoring if running
        if self.monitoring:
            self.stop_monitoring()
        
        # Cleanup
        try:
            self.trading_system.trade_logger.cleanup_old_data()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        
        self.print_success("TradeX shutdown complete. Goodbye!")
        time.sleep(2)
