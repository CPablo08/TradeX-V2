import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import joblib
import os
from loguru import logger
from config import Config
import warnings
warnings.filterwarnings('ignore')

# Optional TensorFlow import
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow is available")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available, using alternative ML libraries")

class MLEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.ensemble_model = None
        self.lstm_model = None
        self.feature_columns = []
        self.is_trained = False
        
        # Create models directory if it doesn't exist
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        
    def prepare_features(self, df, patterns):
        """Prepare features for ML model training"""
        try:
            # Select relevant features for pattern recognition
            feature_cols = [
                # Price action features
                'price_change', 'price_change_2h', 'price_change_4h', 'price_change_24h',
                'high_low_ratio', 'body_size', 'upper_shadow', 'lower_shadow',
                
                # Technical indicators
                'rsi', 'stoch', 'stoch_signal', 'williams_r', 'cci',
                'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_position',
                'atr', 'adx', 'trend_strength',
                
                # Volume features
                'volume_ratio', 'obv', 'vwap',
                
                # Support/Resistance
                'distance_to_support', 'distance_to_resistance',
                
                # Pattern features
                'higher_high', 'lower_low', 'higher_close',
                
                # Volatility features
                'volatility', 'volatility_ratio'
            ]
            
            # Add pattern indicators as features
            pattern_features = []
            for pattern_name, pattern_detected in patterns.items():
                pattern_features.append(pattern_detected)
                feature_cols.append(f'pattern_{pattern_name}')
            
            # Create feature dataframe
            features_df = df[feature_cols].copy()
            
            # Add pattern features
            for i, pattern_name in enumerate(patterns.keys()):
                features_df[f'pattern_{pattern_name}'] = pattern_features[i]
            
            # Add lagged features for time series analysis
            for col in feature_cols[:20]:  # Use first 20 features for lagging
                if col in features_df.columns:
                    features_df[f'{col}_lag1'] = features_df[col].shift(1)
                    features_df[f'{col}_lag2'] = features_df[col].shift(2)
                    features_df[f'{col}_lag4'] = features_df[col].shift(4)
            
            # Add rolling statistics
            for col in ['price_change', 'rsi', 'volume_ratio']:
                if col in features_df.columns:
                    features_df[f'{col}_rolling_mean'] = features_df[col].rolling(window=5).mean()
                    features_df[f'{col}_rolling_std'] = features_df[col].rolling(window=5).std()
            
            # Create target variable (future price movement)
            features_df['future_return'] = df['close'].pct_change(Config.PREDICTION_HORIZON).shift(-Config.PREDICTION_HORIZON)
            features_df['target'] = np.where(features_df['future_return'] > 0.01, 1, 0)  # 1% threshold
            
            # Remove rows with NaN values
            features_df = features_df.dropna()
            
            self.feature_columns = [col for col in features_df.columns if col not in ['future_return', 'target']]
            
            return features_df
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def train_ensemble_model(self, features_df):
        """Train ensemble model combining multiple algorithms"""
        try:
            X = features_df[self.feature_columns]
            y = features_df['target']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train multiple models
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
                'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'xgboost': xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
            }
            
            trained_models = {}
            scores = {}
            
            for name, model in models.items():
                logger.info(f"Training {name}...")
                model.fit(X_train_scaled, y_train)
                score = model.score(X_test_scaled, y_test)
                scores[name] = score
                trained_models[name] = model
                logger.info(f"{name} accuracy: {score:.4f}")
            
            # Create ensemble prediction function
            def ensemble_predict(X):
                predictions = []
                X_scaled = self.scaler.transform(X)
                
                for model in trained_models.values():
                    pred = model.predict_proba(X_scaled)[:, 1]  # Probability of positive class
                    predictions.append(pred)
                
                # Average predictions
                ensemble_pred = np.mean(predictions, axis=0)
                return ensemble_pred
            
            self.ensemble_model = {
                'models': trained_models,
                'predict': ensemble_predict,
                'scores': scores
            }
            
            # Save models
            joblib.dump(self.scaler, Config.FEATURE_SCALER_PATH)
            joblib.dump(self.ensemble_model, Config.ENSEMBLE_MODEL_PATH)
            
            self.is_trained = True
            logger.info("Ensemble model trained and saved successfully")
            
            return scores
            
        except Exception as e:
            logger.error(f"Error training ensemble model: {e}")
            return None
    
    def train_lstm_model(self, features_df):
        """Train LSTM model for sequence prediction"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, skipping LSTM training")
            logger.info("Using ensemble models only")
            return None
        
        try:
            X = features_df[self.feature_columns].values
            y = features_df['target'].values
            
            # Reshape data for LSTM (samples, timesteps, features)
            timesteps = 10
            X_sequences = []
            y_sequences = []
            
            for i in range(timesteps, len(X)):
                X_sequences.append(X[i-timesteps:i])
                y_sequences.append(y[i])
            
            X_sequences = np.array(X_sequences)
            y_sequences = np.array(y_sequences)
            
            # Split data
            split_idx = int(0.8 * len(X_sequences))
            X_train, X_test = X_sequences[:split_idx], X_sequences[split_idx:]
            y_train, y_test = y_sequences[:split_idx], y_sequences[split_idx:]
            
            # Scale features
            X_train_reshaped = X_train.reshape(-1, X_train.shape[-1])
            X_test_reshaped = X_test.reshape(-1, X_test.shape[-1])
            
            X_train_scaled = self.scaler.fit_transform(X_train_reshaped)
            X_test_scaled = self.scaler.transform(X_test_reshaped)
            
            X_train_scaled = X_train_scaled.reshape(X_train.shape)
            X_test_scaled = X_test_scaled.reshape(X_test.shape)
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(timesteps, X_train.shape[2])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1, activation='sigmoid')
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            
            # Train model
            history = model.fit(
                X_train_scaled, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test_scaled, y_test),
                verbose=1
            )
            
            self.lstm_model = model
            
            # Save model
            model.save(Config.LSTM_MODEL_PATH)
            
            logger.info("LSTM model trained and saved successfully")
            
            return history
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            return None
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            if os.path.exists(Config.FEATURE_SCALER_PATH):
                self.scaler = joblib.load(Config.FEATURE_SCALER_PATH)
                logger.info("Feature scaler loaded")
            
            if os.path.exists(Config.ENSEMBLE_MODEL_PATH):
                self.ensemble_model = joblib.load(Config.ENSEMBLE_MODEL_PATH)
                logger.info("Ensemble model loaded")
            
            if os.path.exists(Config.LSTM_MODEL_PATH) and TENSORFLOW_AVAILABLE:
                try:
                    from tensorflow.keras.models import load_model
                    self.lstm_model = load_model(Config.LSTM_MODEL_PATH)
                    logger.info("LSTM model loaded")
                except Exception as e:
                    logger.warning(f"Could not load LSTM model: {e}")
            elif os.path.exists(Config.LSTM_MODEL_PATH) and not TENSORFLOW_AVAILABLE:
                logger.warning("LSTM model exists but TensorFlow not available")
            else:
                logger.info("No LSTM model found")
            
            self.is_trained = True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict(self, features_df):
        """Make predictions using trained models"""
        if not self.is_trained:
            logger.warning("Models not trained. Please train models first.")
            return None
        
        try:
            X = features_df[self.feature_columns].iloc[-1:].values  # Latest data point
            
            predictions = {}
            
            # Ensemble prediction
            if self.ensemble_model:
                ensemble_prob = self.ensemble_model['predict'](X)[0]
                predictions['ensemble_probability'] = ensemble_prob
                predictions['ensemble_signal'] = 1 if ensemble_prob > 0.6 else (-1 if ensemble_prob < 0.4 else 0)
            
            # LSTM prediction
            if self.lstm_model and TENSORFLOW_AVAILABLE:
                try:
                    # Prepare sequence for LSTM
                    timesteps = 10
                    if len(features_df) >= timesteps:
                        X_sequence = features_df[self.feature_columns].iloc[-timesteps:].values
                        X_scaled = self.scaler.transform(X_sequence)
                        X_reshaped = X_scaled.reshape(1, timesteps, X_scaled.shape[1])
                        
                        lstm_prob = self.lstm_model.predict(X_reshaped)[0][0]
                        predictions['lstm_probability'] = lstm_prob
                        predictions['lstm_signal'] = 1 if lstm_prob > 0.6 else (-1 if lstm_prob < 0.4 else 0)
                except Exception as e:
                    logger.warning(f"LSTM prediction failed: {e}")
            else:
                logger.info("LSTM model not available, using ensemble only")
            
            # Combined signal
            if 'ensemble_probability' in predictions and 'lstm_probability' in predictions:
                combined_prob = (predictions['ensemble_probability'] + predictions['lstm_probability']) / 2
                predictions['combined_probability'] = combined_prob
                predictions['combined_signal'] = 1 if combined_prob > 0.6 else (-1 if combined_prob < 0.4 else 0)
            elif 'ensemble_probability' in predictions:
                # Use ensemble only if LSTM not available
                predictions['combined_probability'] = predictions['ensemble_probability']
                predictions['combined_signal'] = predictions['ensemble_signal']
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return None
    
    def get_feature_importance(self):
        """Get feature importance from Random Forest model"""
        if not self.is_trained or not self.ensemble_model:
            return None
        
        try:
            rf_model = self.ensemble_model['models']['random_forest']
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df.head(20)  # Top 20 features
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None
    
    def evaluate_model_performance(self, features_df):
        """Evaluate model performance on historical data"""
        if not self.is_trained:
            return None
        
        try:
            # Use last 20% of data for evaluation
            eval_size = int(len(features_df) * 0.2)
            eval_df = features_df.tail(eval_size)
            
            predictions = []
            actuals = []
            
            for i in range(len(eval_df)):
                if i < 10:  # Skip first few rows for LSTM
                    continue
                    
                current_data = features_df.iloc[:len(features_df)-eval_size+i+1]
                pred = self.predict(current_data)
                
                if pred and 'combined_signal' in pred:
                    predictions.append(pred['combined_signal'])
                    actuals.append(eval_df.iloc[i]['target'])
            
            if len(predictions) > 0:
                # Calculate metrics
                correct_predictions = sum(1 for p, a in zip(predictions, actuals) if p == a)
                accuracy = correct_predictions / len(predictions)
                
                # Calculate returns
                returns = []
                for i, (pred, actual) in enumerate(zip(predictions, actuals)):
                    if pred == 1:  # Buy signal
                        future_return = eval_df.iloc[i]['future_return']
                        returns.append(future_return)
                
                avg_return = np.mean(returns) if returns else 0
                
                return {
                    'accuracy': accuracy,
                    'total_predictions': len(predictions),
                    'buy_signals': sum(1 for p in predictions if p == 1),
                    'sell_signals': sum(1 for p in predictions if p == -1),
                    'hold_signals': sum(1 for p in predictions if p == 0),
                    'average_return_per_trade': avg_return
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error evaluating model performance: {e}")
            return None
