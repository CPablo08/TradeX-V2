"""
TradeX V3 - ML Predictor Module
Lightweight LSTM model for short-term BTC price prediction
Input: Last 24h BTC price data
Output: Signal → BUY, SELL, HOLD
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
import logging
import joblib
import os
from datetime import datetime, timedelta
from config import Config

class MLPredictor:
    def __init__(self):
        """Initialize ML Predictor"""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Model parameters
        self.lookback_hours = self.config.ML_LOOKBACK_HOURS
        self.prediction_horizon = self.config.ML_PREDICTION_HORIZON
        self.confidence_threshold = self.config.ML_CONFIDENCE_THRESHOLD
        
        # Model components
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        
        # Ensemble models
        self.models = {}
        self.scalers = {}
        
        # Initialize ensemble models
        if hasattr(self.config, 'ENSEMBLE_MODELS') and self.config.ENSEMBLE_MODELS:
            for i, model_type in enumerate(self.config.MODEL_TYPES):
                self.models[model_type] = None
                self.scalers[model_type] = MinMaxScaler()
        
        # Load existing model if available
        self.load_model()
        
        self.logger.info("ML Predictor initialized with ensemble models")
    
    def prepare_data(self, df):
        """Prepare data for LSTM model"""
        try:
            if df is None or df.empty:
                return None, None
            
            # Select features for prediction
            features = ['close', 'volume', 'rsi', 'macd', 'bb_position']
            available_features = [f for f in features if f in df.columns]
            
            if len(available_features) < 2:
                self.logger.warning("Insufficient features for ML prediction")
                return None, None
            
            # Create feature matrix
            data = df[available_features].values
            
            # Remove any NaN values
            data = data[~np.isnan(data).any(axis=1)]
            
            if len(data) < self.lookback_hours + 1:
                self.logger.warning("Insufficient data for prediction")
                return None, None
            
            # Scale the data
            scaled_data = self.scaler.fit_transform(data)
            
            # Create sequences for LSTM
            X, y = [], []
            for i in range(self.lookback_hours, len(scaled_data)):
                X.append(scaled_data[i-self.lookback_hours:i])
                # Target: 1 if price goes up, 0 if down
                if i < len(scaled_data) - 1:
                    future_price = scaled_data[i+1, 0]  # close price
                    current_price = scaled_data[i, 0]
                    y.append(1 if future_price > current_price else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            return None, None
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        try:
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1, activation='sigmoid')
            ])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            return model
            
        except Exception as e:
            self.logger.error(f"Error building model: {e}")
            return None
    
    def train_model(self, df):
        """Train the LSTM model"""
        try:
            self.logger.info("Starting model training...")
            
            # Prepare data
            X, y = self.prepare_data(df)
            if X is None or y is None:
                self.logger.error("Failed to prepare data for training")
                return False
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Build model
            self.model = self.build_model((X.shape[1], X.shape[2]))
            if self.model is None:
                return False
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=50,
                batch_size=32,
                verbose=0
            )
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            y_pred_binary = (y_pred > 0.5).astype(int)
            accuracy = accuracy_score(y_test, y_pred_binary)
            
            self.logger.info(f"Model training completed. Accuracy: {accuracy:.4f}")
            
            # Save model
            self.save_model()
            self.is_trained = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False
    
    def predict(self, df):
        """Make prediction on current data"""
        try:
            if not self.is_trained or self.model is None:
                self.logger.warning("Model not trained. Training now...")
                if not self.train_model(df):
                    return None
            
            # Prepare data for prediction
            X, _ = self.prepare_data(df)
            if X is None or len(X) == 0:
                return None
            
            # Get latest sequence
            latest_sequence = X[-1:]
            
            # Make prediction
            prediction = self.model.predict(latest_sequence, verbose=0)
            confidence = prediction[0][0]
            
            # Determine signal
            if confidence > 0.5 + (1 - self.confidence_threshold) / 2:
                signal = 'BUY'
                signal_strength = confidence
            elif confidence < 0.5 - (1 - self.confidence_threshold) / 2:
                signal = 'SELL'
                signal_strength = 1 - confidence
            else:
                signal = 'HOLD'
                signal_strength = 0.5
            
            result = {
                'signal': signal,
                'confidence': confidence,
                'signal_strength': signal_strength,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"Prediction: {signal} (confidence: {confidence:.4f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            return None
    
    def retrain_model(self, df):
        """Retrain model with new data"""
        try:
            self.logger.info("Retraining model with new data...")
            return self.train_model(df)
        except Exception as e:
            self.logger.error(f"Error retraining model: {e}")
            return False
    
    def save_model(self):
        """Save trained model and scaler"""
        try:
            if self.model is not None:
                self.model.save('models/lstm_model.h5')
                joblib.dump(self.scaler, 'models/scaler.pkl')
                self.logger.info("Model saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load existing trained model"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs('models', exist_ok=True)
            
            model_path = 'models/lstm_model.h5'
            scaler_path = 'models/scaler.pkl'
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = tf.keras.models.load_model(model_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                self.logger.info("Existing model loaded successfully")
            else:
                self.logger.info("No existing model found. Will train new model.")
                
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.is_trained = False
    
    def get_model_info(self):
        """Get model information"""
        return {
            'is_trained': self.is_trained,
            'lookback_hours': self.lookback_hours,
            'prediction_horizon': self.prediction_horizon,
            'confidence_threshold': self.confidence_threshold,
            'model_architecture': 'LSTM' if self.model else None
        }
