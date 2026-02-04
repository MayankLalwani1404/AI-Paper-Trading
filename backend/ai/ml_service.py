"""
ML Service Integration
Integrates trained models with FastAPI backend
Provides endpoints for model predictions and management
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple
import logging
from datetime import datetime
import asyncio
import shap
from pathlib import Path
import json

from backend.ai.data_loader import DataLoader
from backend.ai.feature_engineering import FeatureEngineer
from backend.ai.ensemble_model import EnsembleModel, ModelVersionManager
from backend.ai.training_pipeline import TrainingPipeline, AntiOverfittingValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLService:
    """
    Main ML service managing all model operations
    Handles: prediction, training, monitoring, explainability
    """
    
    def __init__(self, model_path: str = "ml_models", data_path: str = "datasets"):
        self.data_loader = DataLoader(data_path)
        self.feature_engineer = FeatureEngineer(lookback=50)
        self.training_pipeline = TrainingPipeline()
        self.model_manager = ModelVersionManager(model_path)

        # Try loading latest model version if available
        self.ensemble_model = None
        try:
            versions = self.model_manager.list_versions()
            if versions:
                latest = sorted(versions)[-1]
                self.ensemble_model = self.model_manager.load_version(latest)
                logger.info(f"Loaded latest model version: {latest}")
        except Exception as e:
            logger.warning(f"No model loaded at startup: {e}")
        self.prediction_cache = {}
        self.performance_metrics = {}
        
        logger.info("ML Service initialized")
    
    # ===== Prediction =====
    
    async def predict(self, symbol: str, timeframe: str = '1d',
                     use_cache: bool = True) -> Dict:
        """
        Make prediction for given symbol
        Returns: signal, confidence, details
        """
        cache_key = f"{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if use_cache and cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        
        try:
            # Load data
            all_data = self.data_loader.load_all_symbols("all")

            if self.ensemble_model is None:
                return {
                    'error': 'Model not trained/loaded. Train first via /ai/train.',
                    'signal': None,
                    'confidence': 0
                }
            
            # Find symbol (case-insensitive)
            symbol_lower = symbol.lower()
            matching_symbol = None
            for key in all_data.keys():
                if key.lower() == symbol_lower:
                    matching_symbol = key
                    break
            
            if not matching_symbol:
                return {
                    'error': f'Symbol {symbol} not found',
                    'signal': None,
                    'confidence': 0
                }
            
            df = all_data[matching_symbol]
            df_resampled = self.data_loader.resample_to_timeframe(df, timeframe)
            
            # Create features
            features = self.feature_engineer.create_features(df_resampled)
            
            # Get OHLCV and TA features
            ohlcv_recent = df_resampled[['Open', 'High', 'Low', 'Close', 'Volume']].tail(60).values
            ta_features_recent = features[self.feature_engineer.get_feature_importance_names()].tail(1).values.flatten()
            
            # Predict
            signal, confidence, details = self.ensemble_model.predict_ensemble(
                ohlcv_recent, ta_features_recent
            )
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'signal': signal,
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat(),
                'details': details,
            }
            
            self.prediction_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Prediction error for {symbol}: {e}")
            return {
                'error': str(e),
                'signal': None,
                'confidence': 0
            }
    
    async def predict_batch(self, symbols: List[str], 
                           timeframe: str = '1d') -> List[Dict]:
        """Make predictions for multiple symbols"""
        tasks = [self.predict(s, timeframe) for s in symbols]
        return await asyncio.gather(*tasks)
    
    # ===== Training =====
    
    async def train_models(self, markets: List[str] = ['US', 'NSE'],
                          epochs: int = 50) -> Dict:
        """
        Train ensemble model on multiple markets
        """
        logger.info(f"Starting training on markets: {markets}")
        
        try:
            # Load data for all symbols in specified markets
            all_symbols = {}
            for market in markets:
                market_data = self.data_loader.load_all_symbols(market)
                all_symbols.update(market_data)
            
            logger.info(f"Loaded {len(all_symbols)} symbols")
            
            # Prepare features for all symbols
            symbols_with_features = {}
            for symbol, df in list(all_symbols.items())[:10]:  # Limit to 10 for demo
                try:
                    df_daily = self.data_loader.resample_to_timeframe(df, '1d')
                    if len(df_daily) > 200:  # Minimum data requirement
                        features = self.feature_engineer.create_features(df_daily)
                        symbols_with_features[symbol] = (df_daily, features)
                except Exception as e:
                    logger.warning(f"Failed to prepare {symbol}: {e}")
            
            logger.info(f"Prepared features for {len(symbols_with_features)} symbols")
            
            # Train ensemble
            if self.ensemble_model is None:
                self.ensemble_model = EnsembleModel()
            
            # Aggregate training data
            X_all, y_all = [], []
            for symbol, (df, features) in symbols_with_features.items():
                X, y = self.training_pipeline.prepare_training_data(df, features)
                X_all.append(X)
                y_all.append(y)
            
            X_train = np.vstack(X_all)
            y_train = np.hstack(y_all)
            
            # Split train/val
            split_idx = int(0.8 * len(X_train))
            X_train_split = X_train[:split_idx]
            y_train_split = y_train[:split_idx]
            X_val = X_train[split_idx:]
            y_val = y_train[split_idx:]
            
            # Train XGBoost (requires no GPU)
            logger.info("Training XGBoost...")
            self.ensemble_model.train_xgboost(X_train_split, y_train_split, X_val, y_val)
            
            # Train LightGBM
            logger.info("Training LightGBM...")
            self.ensemble_model.train_lightgbm(X_train_split, y_train_split, X_val, y_val)
            
            # Save model
            version_tag = self.model_manager.save_version(self.ensemble_model)
            
            return {
                'status': 'success',
                'version': version_tag,
                'symbols_trained': len(symbols_with_features),
                'total_samples': len(X_train),
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
            }
    
    # ===== Model Management =====
    
    def set_active_model(self, version: str) -> Dict:
        """Activate specific model version"""
        try:
            self.ensemble_model = self.model_manager.load_version(version)
            return {
                'status': 'success',
                'active_version': version,
            }
        except Exception as e:
            logger.error(f"Failed to load model version {version}: {e}")
            return {
                'status': 'error',
                'error': str(e),
            }
    
    def list_model_versions(self) -> List[str]:
        """List available model versions"""
        return self.model_manager.list_versions()
    
    # ===== Explainability =====
    
    def explain_prediction(self, symbol: str, timeframe: str = '1d',
                          num_features: int = 10) -> Dict:
        """
        Explain prediction using SHAP values
        Returns: feature importance for the prediction
        """
        try:
            all_data = self.data_loader.load_all_symbols("all")
            df = all_data[symbol]
            df_resampled = self.data_loader.resample_to_timeframe(df, timeframe)
            features = self.feature_engineer.create_features(df_resampled)
            
            # Get last sample
            X_recent = features[self.feature_engineer.get_feature_importance_names()].tail(1).values
            
            # Use SHAP for explainability
            if self.ensemble_model and self.ensemble_model.xgb_model:
                try:
                    import shap
                    explainer = shap.TreeExplainer(self.ensemble_model.xgb_model)
                    shap_values = explainer.shap_values(X_recent)
                    
                    # Get top features
                    feature_names = self.feature_engineer.get_feature_importance_names()
                    importances = {}
                    
                    # Mean SHAP values across classes
                    mean_shap = np.abs(shap_values[0]).mean(axis=0) if isinstance(shap_values, list) else np.abs(shap_values[0])
                    
                    for i, name in enumerate(feature_names):
                        if i < len(mean_shap):
                            importances[name] = float(mean_shap[i])
                    
                    # Sort and return top N
                    top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:num_features]
                    
                    return {
                        'symbol': symbol,
                        'top_features': [{'name': f, 'importance': v} for f, v in top_features],
                        'method': 'SHAP',
                    }
                except ImportError:
                    logger.warning("SHAP not installed, returning feature importance instead")
            
            # Fallback: use model feature importance
            if self.ensemble_model and self.ensemble_model.feature_importance:
                xgb_importance = self.ensemble_model.feature_importance.get('xgb', {})
                top_features = sorted(xgb_importance.items(), key=lambda x: x[1], reverse=True)[:num_features]
                
                return {
                    'symbol': symbol,
                    'top_features': [{'name': f, 'importance': v} for f, v in top_features],
                    'method': 'XGBoost Feature Importance',
                }
            
            return {
                'error': 'No model available for explanation',
                'symbol': symbol,
            }
            
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            return {
                'error': str(e),
                'symbol': symbol,
            }
    
    # ===== Performance Monitoring =====
    
    def evaluate_model(self, symbol: str, timeframe: str = '1d') -> Dict:
        """Evaluate model performance on symbol"""
        try:
            all_data = self.data_loader.load_all_symbols("all")
            df = all_data[symbol]
            df_resampled = self.data_loader.resample_to_timeframe(df, timeframe)
            features = self.feature_engineer.create_features(df_resampled)
            
            # Prepare data
            X, y = self.training_pipeline.prepare_training_data(df_resampled, features)
            
            # Split test set
            test_size = int(0.2 * len(X))
            X_test = X[-test_size:]
            y_test = y[-test_size:]
            
            # Evaluate
            if self.ensemble_model and self.ensemble_model.xgb_model:
                y_pred = np.argmax(self.ensemble_model.xgb_model.predict(X_test), axis=1)
                accuracy = (y_pred == y_test).mean()
                
                return {
                    'symbol': symbol,
                    'accuracy': float(accuracy),
                    'samples': len(y_test),
                    'timestamp': datetime.now().isoformat(),
                }
            
            return {'error': 'No model loaded', 'symbol': symbol}
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {'error': str(e), 'symbol': symbol}
    
    # ===== Retraining =====
    
    async def incremental_retrain(self, new_data_symbols: List[str]) -> Dict:
        """
        Retrain model with new data (incremental learning)
        """
        logger.info(f"Starting incremental retraining on {len(new_data_symbols)} symbols")
        
        try:
            # Load new data
            all_data = self.data_loader.load_all_symbols("all")
            
            X_new_all, y_new_all = [], []
            for symbol in new_data_symbols:
                if symbol in all_data:
                    df = all_data[symbol]
                    df_daily = self.data_loader.resample_to_timeframe(df, '1d')
                    features = self.feature_engineer.create_features(df_daily)
                    
                    X, y = self.training_pipeline.prepare_training_data(df_daily, features)
                    X_new_all.append(X[-100:])  # Last 100 samples (recent data)
                    y_new_all.append(y[-100:])
            
            if not X_new_all:
                return {'error': 'No valid data for retraining'}
            
            X_new = np.vstack(X_new_all)
            y_new = np.hstack(y_new_all)
            
            # Experience replay to prevent forgetting
            X_combined, y_combined = self.training_pipeline.incremental_learner.experience_replay(
                (np.zeros((0, X_new.shape[1])), np.zeros(0, dtype=int)),
                (X_new, y_new),
                replay_ratio=0.3
            )
            
            # Retrain XGBoost
            self.ensemble_model.train_xgboost(X_combined, y_combined)
            
            # Save new version
            version_tag = self.model_manager.save_version(self.ensemble_model, tag=f"incremental_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            return {
                'status': 'success',
                'version': version_tag,
                'new_samples': len(X_new),
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Incremental retraining failed: {e}")
            return {'status': 'error', 'error': str(e)}


# Global ML service instance
ml_service = None

def get_ml_service() -> MLService:
    """Get or create global ML service"""
    global ml_service
    if ml_service is None:
        ml_service = MLService()
    return ml_service


if __name__ == "__main__":
    service = MLService()
    logger.info("ML Service ready for integration with FastAPI")
