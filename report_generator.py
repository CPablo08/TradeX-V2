#!/usr/bin/env python3
"""
TradeX PDF Report Generator
Generates comprehensive PDF reports with trading performance metrics, graphs, and analysis
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
from loguru import logger
import glob
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TradeXReportGenerator:
    def __init__(self, days_back=30):
        self.days_back = days_back
        self.start_date = datetime.now() - timedelta(days=days_back)
        self.end_date = datetime.now()
        self.report_data = {}
        self.trades_data = []
        self.portfolio_data = []
        
    def load_trading_data(self):
        """Load trading data from logs and state files"""
        print("📊 Loading trading data...")
        
        # Load system state
        if os.path.exists('system_state.json'):
            try:
                with open('system_state.json', 'r') as f:
                    self.report_data['current_state'] = json.load(f)
                print("✅ Loaded current system state")
            except Exception as e:
                print(f"⚠️ Could not load system state: {e}")
        
        # Load log files
        log_files = glob.glob('logs/*.log')
        if not log_files:
            print("⚠️ No log files found")
            return False
            
        print(f"📁 Found {len(log_files)} log files")
        
        # Parse trading data from logs
        self.parse_log_files(log_files)
        
        # Load backtest results if available
        self.load_backtest_data()
        
        return True
    
    def parse_log_files(self, log_files):
        """Parse trading data from log files"""
        print("📋 Parsing log files...")
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    # Parse trade entries
                    if 'TRADING SIGNAL:' in line or 'PAPER TRADE:' in line:
                        self.parse_trade_line(line)
                    
                    # Parse portfolio updates
                    elif 'Portfolio Value:' in line:
                        self.parse_portfolio_line(line)
                    
                    # Parse system status
                    elif 'SYSTEM STATUS REPORT' in line:
                        self.parse_system_status(line)
                        
            except Exception as e:
                print(f"⚠️ Error parsing {log_file}: {e}")
    
    def parse_trade_line(self, line):
        """Parse individual trade from log line"""
        try:
            # Extract trade information
            if 'TRADING SIGNAL:' in line:
                # Real trading
                parts = line.split('TRADING SIGNAL:')[1].strip()
                symbol = parts.split()[0]
                direction = parts.split()[1]
                amount = float(parts.split('$')[1].split()[0])
                confidence = float(parts.split('confidence:')[1].split(')')[0])
                
                trade = {
                    'timestamp': self.extract_timestamp(line),
                    'symbol': symbol,
                    'direction': direction.lower(),
                    'amount': amount,
                    'confidence': confidence,
                    'type': 'real'
                }
            else:
                # Paper trading
                parts = line.split('PAPER TRADE:')[1].strip()
                symbol = parts.split()[0]
                direction = parts.split()[1]
                amount = float(parts.split('$')[1].split()[0])
                price = float(parts.split('@ $')[1].split()[0])
                
                trade = {
                    'timestamp': self.extract_timestamp(line),
                    'symbol': symbol,
                    'direction': direction.lower(),
                    'amount': amount,
                    'price': price,
                    'type': 'paper'
                }
            
            # Only include trades from the last month
            if trade['timestamp'] and trade['timestamp'] >= self.start_date:
                self.trades_data.append(trade)
                
        except Exception as e:
            print(f"⚠️ Error parsing trade line: {e}")
    
    def parse_portfolio_line(self, line):
        """Parse portfolio value from log line"""
        try:
            timestamp = self.extract_timestamp(line)
            if not timestamp or timestamp < self.start_date:
                return
                
            # Extract portfolio value
            value_str = line.split('Portfolio Value: $')[1].split()[0]
            value = float(value_str)
            
            self.portfolio_data.append({
                'timestamp': timestamp,
                'value': value
            })
            
        except Exception as e:
            print(f"⚠️ Error parsing portfolio line: {e}")
    
    def parse_system_status(self, line):
        """Parse system status from log line"""
        try:
            timestamp = self.extract_timestamp(line)
            if not timestamp or timestamp < self.start_date:
                return
                
            # Extract system metrics
            if 'Daily Trades:' in line:
                trades_info = line.split('Daily Trades:')[1].split()[0]
                daily_trades = int(trades_info.split('/')[0])
                
                self.report_data.setdefault('system_metrics', []).append({
                    'timestamp': timestamp,
                    'daily_trades': daily_trades
                })
                
        except Exception as e:
            print(f"⚠️ Error parsing system status: {e}")
    
    def extract_timestamp(self, line):
        """Extract timestamp from log line"""
        try:
            # Look for timestamp pattern in log line
            if '[' in line and ']' in line:
                timestamp_str = line.split('[')[1].split(']')[0]
                return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except:
            pass
        return None
    
    def load_backtest_data(self):
        """Load backtest results if available"""
        backtest_files = glob.glob('backtest_results/*.json')
        if backtest_files:
            try:
                with open(backtest_files[-1], 'r') as f:  # Load most recent
                    self.report_data['backtest'] = json.load(f)
                print("✅ Loaded backtest data")
            except Exception as e:
                print(f"⚠️ Could not load backtest data: {e}")
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        print("📈 Calculating performance metrics...")
        
        if not self.trades_data:
            print("⚠️ No trading data found")
            return
        
        # Convert to DataFrame
        trades_df = pd.DataFrame(self.trades_data)
        portfolio_df = pd.DataFrame(self.portfolio_data) if self.portfolio_data else pd.DataFrame()
        
        # Basic metrics
        total_trades = len(trades_df)
        buy_trades = len(trades_df[trades_df['direction'] == 'buy'])
        sell_trades = len(trades_df[trades_df['direction'] == 'sell'])
        
        # Calculate P&L (simplified - would need more data for accurate calculation)
        if not portfolio_df.empty:
            initial_value = portfolio_df.iloc[0]['value']
            final_value = portfolio_df.iloc[-1]['value']
            total_pnl = final_value - initial_value
            total_pnl_percentage = (total_pnl / initial_value) * 100
        else:
            total_pnl = 0
            total_pnl_percentage = 0
        
        # Trading frequency
        if len(trades_df) > 1:
            first_trade = trades_df['timestamp'].min()
            last_trade = trades_df['timestamp'].max()
            trading_days = (last_trade - first_trade).days + 1
            avg_trades_per_day = total_trades / trading_days
        else:
            avg_trades_per_day = 0
        
        # Symbol analysis
        symbol_stats = trades_df.groupby('symbol').agg({
            'direction': 'count',
            'amount': 'sum',
            'confidence': 'mean'
        }).round(2)
        
        # Store metrics
        self.report_data['metrics'] = {
            'period': {
                'start_date': self.start_date.strftime('%Y-%m-%d'),
                'end_date': self.end_date.strftime('%Y-%m-%d'),
                'days': self.days_back
            },
            'trading': {
                'total_trades': total_trades,
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'avg_trades_per_day': round(avg_trades_per_day, 2)
            },
            'performance': {
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percentage': round(total_pnl_percentage, 2),
                'initial_value': initial_value if not portfolio_df.empty else 0,
                'final_value': final_value if not portfolio_df.empty else 0
            },
            'symbol_analysis': symbol_stats.to_dict('index')
        }
        
        print(f"✅ Calculated metrics for {total_trades} trades")
    
    def create_plots(self):
        """Create comprehensive plots for the report"""
        print("📊 Creating plots...")
        
        if not self.trades_data:
            print("⚠️ No data for plots")
            return
        
        trades_df = pd.DataFrame(self.trades_data)
        portfolio_df = pd.DataFrame(self.portfolio_data) if self.portfolio_data else pd.DataFrame()
        
        # Create figure with subplots
        fig = plt.figure(figsize=(15, 20))
        
        # 1. Trading Activity Over Time
        plt.subplot(4, 2, 1)
        if not trades_df.empty:
            trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
            daily_trades = trades_df.groupby('date').size()
            plt.plot(daily_trades.index, daily_trades.values, marker='o', linewidth=2)
            plt.title('Daily Trading Activity', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Number of Trades')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 2. Portfolio Value Over Time
        plt.subplot(4, 2, 2)
        if not portfolio_df.empty:
            portfolio_df['date'] = pd.to_datetime(portfolio_df['timestamp']).dt.date
            portfolio_df = portfolio_df.groupby('date')['value'].last()
            plt.plot(portfolio_df.index, portfolio_df.values, marker='o', linewidth=2, color='green')
            plt.title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Portfolio Value ($)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        # 3. Trade Distribution by Symbol
        plt.subplot(4, 2, 3)
        if not trades_df.empty:
            symbol_counts = trades_df['symbol'].value_counts()
            plt.pie(symbol_counts.values, labels=symbol_counts.index, autopct='%1.1f%%', startangle=90)
            plt.title('Trade Distribution by Symbol', fontsize=14, fontweight='bold')
        
        # 4. Trade Direction Distribution
        plt.subplot(4, 2, 4)
        if not trades_df.empty:
            direction_counts = trades_df['direction'].value_counts()
            colors = ['green' if x == 'buy' else 'red' for x in direction_counts.index]
            plt.bar(direction_counts.index, direction_counts.values, color=colors)
            plt.title('Trade Direction Distribution', fontsize=14, fontweight='bold')
            plt.ylabel('Number of Trades')
        
        # 5. Trade Amount Distribution
        plt.subplot(4, 2, 5)
        if not trades_df.empty:
            plt.hist(trades_df['amount'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Trade Amount Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Trade Amount ($)')
            plt.ylabel('Frequency')
        
        # 6. Confidence Score Distribution
        plt.subplot(4, 2, 6)
        if not trades_df.empty and 'confidence' in trades_df.columns:
            confidence_data = trades_df['confidence'].dropna()
            if len(confidence_data) > 0:
                plt.hist(confidence_data, bins=15, alpha=0.7, color='orange', edgecolor='black')
                plt.title('ML Confidence Score Distribution', fontsize=14, fontweight='bold')
                plt.xlabel('Confidence Score')
                plt.ylabel('Frequency')
        
        # 7. Hourly Trading Activity
        plt.subplot(4, 2, 7)
        if not trades_df.empty:
            trades_df['hour'] = pd.to_datetime(trades_df['timestamp']).dt.hour
            hourly_trades = trades_df.groupby('hour').size()
            plt.bar(hourly_trades.index, hourly_trades.values, alpha=0.7, color='purple')
            plt.title('Hourly Trading Activity', fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Trades')
            plt.xticks(range(0, 24, 2))
        
        # 8. Cumulative P&L (if portfolio data available)
        plt.subplot(4, 2, 8)
        if not portfolio_df.empty:
            portfolio_df['date'] = pd.to_datetime(portfolio_df['timestamp']).dt.date
            portfolio_df = portfolio_df.groupby('date')['value'].last()
            initial_value = portfolio_df.iloc[0]
            cumulative_pnl = portfolio_df - initial_value
            plt.plot(cumulative_pnl.index, cumulative_pnl.values, marker='o', linewidth=2, color='red')
            plt.title('Cumulative P&L Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Cumulative P&L ($)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.report_data['plots'] = fig
        
        print("✅ Created comprehensive plots")
    
    def generate_pdf_report(self, filename=None):
        """Generate the complete PDF report"""
        if filename is None:
            filename = f"TradeX_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        print(f"📄 Generating PDF report: {filename}")
        
        # Calculate metrics
        self.calculate_performance_metrics()
        
        # Create plots
        self.create_plots()
        
        # Generate PDF
        with PdfPages(filename) as pdf:
            # Title page
            self.create_title_page(pdf)
            
            # Executive Summary
            self.create_executive_summary(pdf)
            
            # Performance Metrics
            self.create_performance_metrics_page(pdf)
            
            # Trading Analysis
            self.create_trading_analysis_page(pdf)
            
            # Plots page
            if 'plots' in self.report_data:
                pdf.savefig(self.report_data['plots'])
                plt.close()
            
            # Detailed Logs
            self.create_detailed_logs_page(pdf)
            
            # System Health
            self.create_system_health_page(pdf)
        
        print(f"✅ PDF report generated: {filename}")
        return filename
    
    def create_title_page(self, pdf):
        """Create the title page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.8, 'TradeX Trading Report', fontsize=24, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        # Subtitle
        ax.text(0.5, 0.7, f'Performance Analysis Report', fontsize=16, 
                ha='center', va='center', transform=ax.transAxes)
        
        # Period
        period_text = f"Period: {self.start_date.strftime('%B %d, %Y')} - {self.end_date.strftime('%B %d, %Y')}"
        ax.text(0.5, 0.6, period_text, fontsize=14, 
                ha='center', va='center', transform=ax.transAxes)
        
        # Generated date
        generated_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}"
        ax.text(0.5, 0.5, generated_text, fontsize=12, 
                ha='center', va='center', transform=ax.transAxes)
        
        # Summary stats
        if 'metrics' in self.report_data:
            metrics = self.report_data['metrics']
            y_pos = 0.35
            
            ax.text(0.5, y_pos, f"Total Trades: {metrics['trading']['total_trades']}", 
                    fontsize=14, ha='center', va='center', transform=ax.transAxes)
            y_pos -= 0.05
            
            ax.text(0.5, y_pos, f"Total P&L: ${metrics['performance']['total_pnl']:,.2f} ({metrics['performance']['total_pnl_percentage']:+.2f}%)", 
                    fontsize=14, ha='center', va='center', transform=ax.transAxes)
            y_pos -= 0.05
            
            if metrics['performance']['final_value'] > 0:
                ax.text(0.5, y_pos, f"Final Portfolio Value: ${metrics['performance']['final_value']:,.2f}", 
                        fontsize=14, ha='center', va='center', transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close()
    
    def create_executive_summary(self, pdf):
        """Create executive summary page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Executive Summary', fontsize=20, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        if 'metrics' in self.report_data:
            metrics = self.report_data['metrics']
            y_pos = 0.85
            
            # Key metrics
            summary_items = [
                f"📊 Trading Period: {metrics['period']['days']} days",
                f"📈 Total Trades: {metrics['trading']['total_trades']}",
                f"💰 Total P&L: ${metrics['performance']['total_pnl']:,.2f}",
                f"📊 P&L Percentage: {metrics['performance']['total_pnl_percentage']:+.2f}%",
                f"🔄 Average Trades/Day: {metrics['trading']['avg_trades_per_day']}",
                f"📈 Buy Trades: {metrics['trading']['buy_trades']}",
                f"📉 Sell Trades: {metrics['trading']['sell_trades']}"
            ]
            
            for item in summary_items:
                ax.text(0.1, y_pos, item, fontsize=12, 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.08
            
            # Performance assessment
            y_pos -= 0.05
            ax.text(0.1, y_pos, 'Performance Assessment:', fontsize=14, fontweight='bold', 
                    ha='left', va='center', transform=ax.transAxes)
            y_pos -= 0.06
            
            if metrics['performance']['total_pnl_percentage'] > 0:
                assessment = "✅ Profitable trading period"
            elif metrics['performance']['total_pnl_percentage'] < 0:
                assessment = "❌ Loss-making trading period"
            else:
                assessment = "➖ Break-even trading period"
            
            ax.text(0.1, y_pos, assessment, fontsize=12, 
                    ha='left', va='center', transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close()
    
    def create_performance_metrics_page(self, pdf):
        """Create detailed performance metrics page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Detailed Performance Metrics', fontsize=20, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        if 'metrics' in self.report_data:
            metrics = self.report_data['metrics']
            y_pos = 0.85
            
            # Performance metrics
            perf_items = [
                f"Initial Portfolio Value: ${metrics['performance']['initial_value']:,.2f}",
                f"Final Portfolio Value: ${metrics['performance']['final_value']:,.2f}",
                f"Total P&L: ${metrics['performance']['total_pnl']:,.2f}",
                f"P&L Percentage: {metrics['performance']['total_pnl_percentage']:+.2f}%",
                f"Trading Days: {metrics['period']['days']}",
                f"Total Trades: {metrics['trading']['total_trades']}",
                f"Average Trades/Day: {metrics['trading']['avg_trades_per_day']}",
                f"Buy Trades: {metrics['trading']['buy_trades']}",
                f"Sell Trades: {metrics['trading']['sell_trades']}"
            ]
            
            for item in perf_items:
                ax.text(0.1, y_pos, item, fontsize=11, 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.06
            
            # Symbol analysis
            if 'symbol_analysis' in metrics:
                y_pos -= 0.05
                ax.text(0.1, y_pos, 'Symbol Analysis:', fontsize=14, fontweight='bold', 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.06
                
                for symbol, data in metrics['symbol_analysis'].items():
                    symbol_text = f"{symbol}: {data['direction']} trades, ${data['amount']:,.2f} total"
                    ax.text(0.1, y_pos, symbol_text, fontsize=10, 
                            ha='left', va='center', transform=ax.transAxes)
                    y_pos -= 0.05
        
        pdf.savefig(fig)
        plt.close()
    
    def create_trading_analysis_page(self, pdf):
        """Create trading analysis page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Trading Analysis', fontsize=20, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        if self.trades_data:
            trades_df = pd.DataFrame(self.trades_data)
            y_pos = 0.85
            
            # Trading patterns
            analysis_items = [
                f"Most Active Symbol: {trades_df['symbol'].mode().iloc[0] if len(trades_df['symbol'].mode()) > 0 else 'N/A'}",
                f"Most Common Direction: {trades_df['direction'].mode().iloc[0] if len(trades_df['direction'].mode()) > 0 else 'N/A'}",
                f"Average Trade Amount: ${trades_df['amount'].mean():,.2f}",
                f"Largest Trade: ${trades_df['amount'].max():,.2f}",
                f"Smallest Trade: ${trades_df['amount'].min():,.2f}"
            ]
            
            for item in analysis_items:
                ax.text(0.1, y_pos, item, fontsize=11, 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.06
            
            # ML confidence analysis
            if 'confidence' in trades_df.columns:
                confidence_data = trades_df['confidence'].dropna()
                if len(confidence_data) > 0:
                    y_pos -= 0.05
                    ax.text(0.1, y_pos, 'ML Confidence Analysis:', fontsize=14, fontweight='bold', 
                            ha='left', va='center', transform=ax.transAxes)
                    y_pos -= 0.06
                    
                    conf_items = [
                        f"Average Confidence: {confidence_data.mean():.2f}",
                        f"Highest Confidence: {confidence_data.max():.2f}",
                        f"Lowest Confidence: {confidence_data.min():.2f}",
                        f"Confidence Std Dev: {confidence_data.std():.2f}"
                    ]
                    
                    for item in conf_items:
                        ax.text(0.1, y_pos, item, fontsize=10, 
                                ha='left', va='center', transform=ax.transAxes)
                        y_pos -= 0.05
        
        pdf.savefig(fig)
        plt.close()
    
    def create_detailed_logs_page(self, pdf):
        """Create detailed logs page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Recent Trading Activity', fontsize=20, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        if self.trades_data:
            # Show last 20 trades
            recent_trades = sorted(self.trades_data, key=lambda x: x['timestamp'])[-20:]
            y_pos = 0.85
            
            for trade in recent_trades:
                trade_text = f"{trade['timestamp'].strftime('%Y-%m-%d %H:%M')} - {trade['symbol']} {trade['direction'].upper()} ${trade['amount']:,.2f}"
                ax.text(0.1, y_pos, trade_text, fontsize=9, 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.04
                
                if y_pos < 0.1:  # Prevent text from going off page
                    break
        
        pdf.savefig(fig)
        plt.close()
    
    def create_system_health_page(self, pdf):
        """Create system health page"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'System Health Summary', fontsize=20, fontweight='bold', 
                ha='center', va='center', transform=ax.transAxes)
        
        y_pos = 0.85
        
        # System status
        if 'current_state' in self.report_data:
            state = self.report_data['current_state']
            
            health_items = [
                f"System Uptime: {state.get('uptime', 'N/A')}",
                f"Emergency Stop: {state.get('emergency_stop', 'N/A')}",
                f"Consecutive Errors: {state.get('consecutive_errors', 'N/A')}",
                f"Active Positions: {len(state.get('active_positions', {}))}",
                f"Daily Trades: {state.get('daily_trades', 'N/A')}"
            ]
            
            for item in health_items:
                ax.text(0.1, y_pos, item, fontsize=11, 
                        ha='left', va='center', transform=ax.transAxes)
                y_pos -= 0.06
        
        # System metrics
        if 'system_metrics' in self.report_data:
            y_pos -= 0.05
            ax.text(0.1, y_pos, 'System Performance:', fontsize=14, fontweight='bold', 
                    ha='left', va='center', transform=ax.transAxes)
            y_pos -= 0.06
            
            metrics = self.report_data['system_metrics']
            if metrics:
                avg_daily_trades = np.mean([m['daily_trades'] for m in metrics])
                ax.text(0.1, y_pos, f"Average Daily Trades: {avg_daily_trades:.1f}", fontsize=11, 
                        ha='left', va='center', transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close()

def main():
    """Main function to generate report"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate TradeX PDF Report')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('--output', type=str, help='Output filename for PDF')
    
    args = parser.parse_args()
    
    print("🚀 TradeX PDF Report Generator")
    print("=" * 50)
    
    # Create report generator
    generator = TradeXReportGenerator(days_back=args.days)
    
    # Load data
    if not generator.load_trading_data():
        print("❌ No trading data found. Make sure you have logs and trading activity.")
        return
    
    # Generate report
    filename = generator.generate_pdf_report(args.output)
    
    print(f"\n🎉 Report generated successfully!")
    print(f"📄 File: {filename}")
    print(f"📊 Period: {generator.start_date.strftime('%Y-%m-%d')} to {generator.end_date.strftime('%Y-%m-%d')}")
    
    if 'metrics' in generator.report_data:
        metrics = generator.report_data['metrics']
        print(f"📈 Total Trades: {metrics['trading']['total_trades']}")
        print(f"💰 Total P&L: ${metrics['performance']['total_pnl']:,.2f}")

if __name__ == "__main__":
    main()
