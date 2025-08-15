#!/usr/bin/env python3
"""
TradeX - Crypto Trading Automation Platform
Main entry point for the trading system
"""

import os
import sys
import argparse
from loguru import logger
from trading_engine import TradingEngine
from train_models import main as train_models
from backtest_engine import BacktestEngine
from config import Config

def setup_logging():
    """Setup logging configuration"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=Config.LOG_LEVEL
    )
    logger.add(
        Config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=Config.LOG_LEVEL,
        rotation="1 day",
        retention="7 days"
    )

def check_environment():
    """Check if environment is properly configured"""
    required_vars = ['CB_API_KEY', 'CB_API_SECRET', 'CB_API_PASSPHRASE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    return True

def run_trading_engine():
    """Run the main trading engine"""
    logger.info("Starting TradeX Trading Engine...")
    
    try:
        engine = TradingEngine()
        engine.run()
    except KeyboardInterrupt:
        logger.info("Trading engine stopped by user")
    except Exception as e:
        logger.error(f"Trading engine error: {e}")
        raise

def run_backtest(args):
    """Run backtesting mode"""
    print("🚀 Starting TradeX Backtest Engine...")
    logger.info("Starting TradeX Backtest Engine...")
    
    try:
        from datetime import datetime
        
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
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        print(f"❌ Backtest error: {e}")
        raise

def run_paper_trading():
    """Run paper trading mode (simulated trading with real data)"""
    print("📝 Starting TradeX Paper Trading Mode...")
    logger.info("Starting TradeX Paper Trading Mode...")
    
    try:
        from trading_engine import TradingEngine
        
        # Create trading engine with paper trading flag
        engine = TradingEngine(paper_trading=True)
        engine.run()
        
    except KeyboardInterrupt:
        logger.info("Paper trading stopped by user")
    except Exception as e:
        logger.error(f"Paper trading error: {e}")
        print(f"❌ Paper trading error: {e}")
        raise

def run_report_generation(args):
    """Generate PDF report with trading performance metrics"""
    print("📄 Starting TradeX Report Generation...")
    logger.info("Starting TradeX Report Generation...")
    
    try:
        from report_generator import TradeXReportGenerator
        
        # Create report generator
        generator = TradeXReportGenerator(days_back=args.days if hasattr(args, 'days') else 30)
        
        # Load data
        if not generator.load_trading_data():
            print("❌ No trading data found. Make sure you have logs and trading activity.")
            return
        
        # Generate report
        filename = generator.generate_pdf_report(args.output if hasattr(args, 'output') else None)
        
        print(f"\n🎉 Report generated successfully!")
        print(f"📄 File: {filename}")
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        print(f"❌ Report generation error: {e}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='TradeX Crypto Trading Platform')
    parser.add_argument('--mode', choices=['trade', 'train', 'backtest', 'paper', 'report'], 
                       default='trade', help='Operation mode')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--paper', action='store_true', 
                       help='Run in paper trading mode (simulated trading)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in dry-run mode (no actual trades)')
    
    # Backtest specific arguments
    parser.add_argument('--start-date', type=str, help='Backtest start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Backtest end date (YYYY-MM-DD)')
    parser.add_argument('--initial-balance', type=float, default=1000, help='Initial balance for backtest')
    
    # Report specific arguments
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze for report (default: 30)')
    parser.add_argument('--output', type=str, help='Output filename for PDF report')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Check environment (skip for backtest mode)
    if args.mode != 'backtest' and not check_environment():
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("TradeX Crypto Trading Platform")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Supported pairs: {', '.join(Config.SUPPORTED_PAIRS)}")
    logger.info(f"Trade amount: ${Config.TRADE_AMOUNT_USD}")
    logger.info(f"Stop loss: {Config.STOP_LOSS_PERCENTAGE*100}%")
    logger.info(f"Take profit: {Config.TAKE_PROFIT_PERCENTAGE*100}%")
    logger.info("=" * 60)
    
    try:
        if args.mode == 'trade':
            if args.paper:
                logger.info("PAPER TRADING MODE - Simulated trading with real data")
                run_paper_trading()
            elif args.dry_run:
                logger.info("DRY RUN MODE - No actual trades will be placed")
                # TODO: Implement dry-run mode
            else:
                run_trading_engine()
        elif args.mode == 'train':
            logger.info("Training ML models...")
            train_models()
        elif args.mode == 'backtest':
            run_backtest(args)
        elif args.mode == 'paper':
            logger.info("PAPER TRADING MODE - Simulated trading with real data")
            run_paper_trading()
        elif args.mode == 'report':
            logger.info("Generating PDF report...")
            run_report_generation(args)
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
