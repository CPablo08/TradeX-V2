#!/usr/bin/env python3
"""
TradeX Model Training Script
Trains ML models using historical data for pattern recognition and price prediction
"""

import os
import sys
import subprocess
from loguru import logger
from data_collector import DataCollector
from ml_engine import MLEngine
from config import Config

def activate_virtual_environment():
    """Automatically activate virtual environment if not already activated"""
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True  # Already in virtual environment
    
    # Check if virtual environment exists
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tradex_env')
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found!")
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
            print("✅ Virtual environment created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    # Get the path to the virtual environment's Python executable
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:  # Unix/Linux/macOS
        python_path = os.path.join(venv_path, 'bin', 'python')
    
    if not os.path.exists(python_path):
        print(f"❌ Python executable not found at: {python_path}")
        return False
    
    # If we're not in the virtual environment, restart with the virtual environment's Python
    if sys.executable != python_path:
        print("🔄 Activating virtual environment...")
        print(f"   Current Python: {sys.executable}")
        print(f"   Virtual Python: {python_path}")
        
        # Restart the script with the virtual environment's Python
        os.execv(python_path, [python_path] + sys.argv)
    
    return True

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

def collect_training_data():
    """Collect historical data for training"""
    logger.info("Collecting training data...")
    
    data_collector = DataCollector()
    all_data = {}
    all_patterns = {}
    
    for symbol in Config.SUPPORTED_PAIRS:
        logger.info(f"Fetching data for {symbol}...")
        
        # Fetch more historical data for training
        df = data_collector.fetch_historical_data(
            symbol, 
            lookback_days=Config.DATA_LOOKBACK_DAYS * 2  # Double the lookback for training
        )
        
        if df is not None:
            # Calculate technical indicators
            df = data_collector.calculate_technical_indicators(df)
            
            # Identify patterns
            patterns = data_collector.identify_chart_patterns(df)
            
            all_data[symbol] = df
            all_patterns[symbol] = patterns
            
            logger.info(f"Collected {len(df)} data points for {symbol}")
        else:
            logger.error(f"Failed to collect data for {symbol}")
    
    return all_data, all_patterns

def prepare_training_features(all_data, all_patterns):
    """Prepare features for model training"""
    logger.info("Preparing training features...")
    
    ml_engine = MLEngine()
    combined_features = []
    
    for symbol in Config.SUPPORTED_PAIRS:
        if symbol in all_data and symbol in all_patterns:
            logger.info(f"Preparing features for {symbol}...")
            
            features_df = ml_engine.prepare_features(all_data[symbol], all_patterns[symbol])
            
            if features_df is not None:
                # Add symbol identifier
                features_df['symbol'] = symbol
                combined_features.append(features_df)
                
                logger.info(f"Prepared {len(features_df)} feature samples for {symbol}")
            else:
                logger.error(f"Failed to prepare features for {symbol}")
    
    if combined_features:
        # Combine all features
        combined_df = pd.concat(combined_features, ignore_index=True)
        logger.info(f"Total training samples: {len(combined_df)}")
        return combined_df
    else:
        logger.error("No features prepared for training")
        return None

def train_models(features_df):
    """Train ML models"""
    logger.info("Starting model training...")
    
    ml_engine = MLEngine()
    
    # Train ensemble model
    logger.info("Training ensemble model...")
    ensemble_scores = ml_engine.train_ensemble_model(features_df)
    
    if ensemble_scores:
        logger.info("Ensemble model training completed:")
        for model_name, score in ensemble_scores.items():
            logger.info(f"  {model_name}: {score:.4f}")
    
    # Train LSTM model
    logger.info("Training LSTM model...")
    lstm_history = ml_engine.train_lstm_model(features_df)
    
    if lstm_history:
        logger.info("LSTM model training completed")
        final_accuracy = lstm_history['accuracy'][-1] if 'accuracy' in lstm_history else 0
        logger.info(f"  Final LSTM accuracy: {final_accuracy:.4f}")
    
    # Get feature importance
    importance_df = ml_engine.get_feature_importance()
    if importance_df is not None:
        logger.info("Top 10 most important features:")
        for _, row in importance_df.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    return ml_engine

def evaluate_models(ml_engine, features_df):
    """Evaluate model performance"""
    logger.info("Evaluating model performance...")
    
    performance = ml_engine.evaluate_model_performance(features_df)
    
    if performance:
        logger.info("Model Performance Results:")
        logger.info(f"  Accuracy: {performance['accuracy']:.4f}")
        logger.info(f"  Total Predictions: {performance['total_predictions']}")
        logger.info(f"  Buy Signals: {performance['buy_signals']}")
        logger.info(f"  Sell Signals: {performance['sell_signals']}")
        logger.info(f"  Hold Signals: {performance['hold_signals']}")
        logger.info(f"  Average Return per Trade: {performance['average_return_per_trade']:.4f}")
    else:
        logger.warning("Could not evaluate model performance")

def main():
    """Main training function"""
    # Activate virtual environment automatically
    if not activate_virtual_environment():
        print("❌ Failed to activate virtual environment. Please run setup_jetson.sh first.")
        sys.exit(1)
    
    setup_logging()
    
    logger.info("Starting TradeX Model Training...")
    
    try:
        # Step 1: Collect training data
        all_data, all_patterns = collect_training_data()
        
        if not all_data:
            logger.error("No data collected. Exiting.")
            return
        
        # Step 2: Prepare features
        features_df = prepare_training_features(all_data, all_patterns)
        
        if features_df is None:
            logger.error("No features prepared. Exiting.")
            return
        
        # Step 3: Train models
        ml_engine = train_models(features_df)
        
        # Step 4: Evaluate models
        evaluate_models(ml_engine, features_df)
        
        logger.info("Model training completed successfully!")
        
        # Save training summary
        training_summary = {
            'training_date': datetime.now().isoformat(),
            'total_samples': len(features_df),
            'symbols_trained': list(all_data.keys()),
            'features_count': len(ml_engine.feature_columns),
            'models_trained': ['ensemble', 'lstm']
        }
        
        import json
        with open('training_summary.json', 'w') as f:
            json.dump(training_summary, f, indent=2)
        
        logger.info("Training summary saved to training_summary.json")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime
    
    main()
