"""
Hybrid Ensemble Model combining CNN, LSTM, and XGBoost/LightGBM
Outputs BUY/SELL/HOLD signal with confidence score and explainability
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Tuple, Optional, List
import logging
from sklearn.ensemble import RandomForestClassifier
import pickle
import json
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleModel:
    """
    Hybrid ensemble combining:
    - CNN: Candlestick pattern recognition (pattern_prob)
    - LSTM: Time series direction prediction (direction_prob)
    - XGBoost: Technical indicator classification (xgb_prob)
    - Final vote: Weighted ensemble → BUY/SELL/HOLD + confidence
    """
    
    def __init__(self, cnn_model=None, lstm_model=None, version: str = "v1.0"):
        self.cnn_model = cnn_model
        self.lstm_model = lstm_model
        self.xgb_model = None
        self.lgb_model = None
        self.version = version
        self.feature_importance = {}
        
        # Weights for ensemble (can be tuned)
        self.cnn_weight = 0.20
        self.lstm_weight = 0.20
        self.xgb_weight = 0.30
        self.lgb_weight = 0.30
        
        logger.info(f"Ensemble Model {version} initialized")
    
    def train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray,
                     X_val: Optional[np.ndarray] = None,
                     y_val: Optional[np.ndarray] = None) -> Dict:
        """Train XGBoost classifier on technical indicators"""
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        
        params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'learning_rate': 0.05,
            'max_depth': 6,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'eval_metric': 'mlogloss',
        }
        
        eval_set = None
        if X_val is not None:
            dval = xgb.DMatrix(X_val, label=y_val)
            eval_set = [(dtrain, 'train'), (dval, 'val')]
        
        self.xgb_model = xgb.train(
            params,
            dtrain,
            num_boost_round=300,
            evals=eval_set,
            early_stopping_rounds=20,
            verbose_eval=False
        )
        
        # Store feature importance
        self.feature_importance['xgb'] = self.xgb_model.get_score(importance_type='weight')
        
        logger.info("XGBoost model trained successfully")
        return {'model': self.xgb_model}
    
    def train_lightgbm(self, X_train: np.ndarray, y_train: np.ndarray,
                      X_val: Optional[np.ndarray] = None,
                      y_val: Optional[np.ndarray] = None) -> Dict:
        """Train LightGBM classifier as alternative/additional model"""
        
        train_data = lgb.Dataset(X_train, label=y_train)
        
        params = {
            'objective': 'multiclass',
            'num_class': 3,
            'learning_rate': 0.05,
            'num_leaves': 31,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'verbose': -1,
        }
        
        valid_sets = [train_data]
        valid_names = ['train']
        callbacks = []
        
        if X_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            valid_names.append('valid')
            callbacks = [lgb.early_stopping(20), lgb.log_evaluation(0)]
        
        self.lgb_model = lgb.train(
            params,
            train_data,
            num_boost_round=300,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=callbacks,
        )
        
        logger.info("LightGBM model trained successfully")
        return {'model': self.lgb_model}
    
    def predict_ensemble(self, ohlcv_sequence: np.ndarray,
                        ta_features: np.ndarray) -> Tuple[str, float, Dict]:
        """
        Ensemble prediction combining all models
        
        Returns:
            signal: 'BUY', 'SELL', 'HOLD'
            confidence: 0-1 confidence score
            details: Dict with individual model probabilities
        """
        
        details = {
            'timestamp': datetime.now().isoformat(),
            'cnn_prob': None,
            'lstm_prob': None,
            'xgb_prob': None,
            'lgb_prob': None,
            'ensemble_prob': None,
        }
        
        # === CNN: Candlestick pattern ===
        cnn_pred = None
        if self.cnn_model is not None:
            # CNN returns pattern class (0-3)
            # Map to signals: 0,1→SELL (bearish), 2→HOLD, 3→BUY (bullish)
            try:
                pattern_class, cnn_conf = self.cnn_model.predict(ohlcv_sequence[-60:])
                if pattern_class in [3, 4]:
                    cnn_pred = np.array([0.1, 0.2, 0.7])  # BUY
                elif pattern_class in [0, 1]:
                    cnn_pred = np.array([0.7, 0.2, 0.1])  # SELL
                else:
                    cnn_pred = np.array([0.33, 0.34, 0.33])  # HOLD
                details['cnn_prob'] = cnn_pred.tolist()
            except Exception as e:
                logger.warning(f"CNN prediction failed: {e}")
                cnn_pred = np.array([0.33, 0.34, 0.33])
        
        # === LSTM: Time series direction ===
        lstm_pred = None
        if self.lstm_model is not None:
            try:
                direction, lstm_conf = self.lstm_model.predict(ohlcv_sequence)
                # direction: 0=down, 1=sideways, 2=up
                lstm_probs = np.zeros(3)
                lstm_probs[direction] = lstm_conf
                lstm_probs[(direction - 1) % 3] = (1 - lstm_conf) / 2
                lstm_probs[(direction + 1) % 3] = (1 - lstm_conf) / 2
                lstm_pred = lstm_probs
                details['lstm_prob'] = lstm_pred.tolist()
            except Exception as e:
                logger.warning(f"LSTM prediction failed: {e}")
                lstm_pred = np.array([0.33, 0.34, 0.33])
        
        # === XGBoost: Technical indicators ===
        xgb_pred = None
        if self.xgb_model is not None:
            try:
                ta_features_xgb = xgb.DMatrix(ta_features.reshape(1, -1))
                xgb_pred = self.xgb_model.predict(ta_features_xgb)[0]
                details['xgb_prob'] = xgb_pred.tolist()
            except Exception as e:
                logger.warning(f"XGBoost prediction failed: {e}")
                xgb_pred = np.array([0.33, 0.34, 0.33])

        # === LightGBM: Technical indicators ===
        lgb_pred = None
        if self.lgb_model is not None:
            try:
                lgb_pred = self.lgb_model.predict(ta_features.reshape(1, -1))[0]
                details['lgb_prob'] = lgb_pred.tolist()
            except Exception as e:
                logger.warning(f"LightGBM prediction failed: {e}")
                lgb_pred = np.array([0.33, 0.34, 0.33])
        
        # === Ensemble voting ===
        ensemble_probs = np.zeros(3)
        total_weight = 0
        
        if cnn_pred is not None:
            ensemble_probs += cnn_pred * self.cnn_weight
            total_weight += self.cnn_weight
        
        if lstm_pred is not None:
            ensemble_probs += lstm_pred * self.lstm_weight
            total_weight += self.lstm_weight
        
        if xgb_pred is not None:
            ensemble_probs += xgb_pred * self.xgb_weight
            total_weight += self.xgb_weight

        if lgb_pred is not None:
            ensemble_probs += lgb_pred * self.lgb_weight
            total_weight += self.lgb_weight
        
        # Normalize
        if total_weight > 0:
            ensemble_probs = ensemble_probs / total_weight
        else:
            ensemble_probs = np.array([0.33, 0.34, 0.33])
        
        details['ensemble_prob'] = ensemble_probs.tolist()
        
        # Decode signal
        signal_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        signal = signal_map[np.argmax(ensemble_probs)]
        confidence = float(np.max(ensemble_probs))
        
        return signal, confidence, details
    
    def set_ensemble_weights(self, cnn_w: float, lstm_w: float, xgb_w: float):
        """Adjust ensemble weights (must sum to 1 for best results)"""
        total = cnn_w + lstm_w + xgb_w
        self.cnn_weight = cnn_w / total
        self.lstm_weight = lstm_w / total
        self.xgb_weight = xgb_w / total
        logger.info(f"Weights updated: CNN={self.cnn_weight:.2f}, LSTM={self.lstm_weight:.2f}, XGB={self.xgb_weight:.2f}")
    
    def save(self, path: str):
        """Save ensemble model to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save XGBoost
        if self.xgb_model:
            self.xgb_model.save_model(os.path.join(path, 'xgb_model.bin'))
        
        # Save LightGBM
        if self.lgb_model:
            self.lgb_model.save_model(os.path.join(path, 'lgb_model.txt'))
        
        # Save metadata
        metadata = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'weights': {
                'cnn': self.cnn_weight,
                'lstm': self.lstm_weight,
                'xgb': self.xgb_weight
            },
            'feature_importance': self.feature_importance
        }
        
        with open(os.path.join(path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Ensemble model saved to {path}")
    
    def load(self, path: str):
        """Load ensemble model from disk"""
        # Load XGBoost
        xgb_path = os.path.join(path, 'xgb_model.bin')
        if os.path.exists(xgb_path):
            self.xgb_model = xgb.Booster()
            self.xgb_model.load_model(xgb_path)
        
        # Load metadata
        metadata_path = os.path.join(path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                self.version = metadata.get('version', self.version)
                weights = metadata.get('weights', {})
                self.set_ensemble_weights(
                    weights.get('cnn', 0.25),
                    weights.get('lstm', 0.35),
                    weights.get('xgb', 0.40)
                )
        
        logger.info(f"Ensemble model loaded from {path}")


class ModelVersionManager:
    """Manages model versions and A/B testing"""
    
    def __init__(self, base_path: str = "ml_models"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self.models = {}
        self.active_model = None
    
    def save_version(self, model: EnsembleModel, tag: str = None):
        """Save model with version tag"""
        if tag is None:
            tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        version_path = os.path.join(self.base_path, tag)
        model.save(version_path)
        
        self.models[tag] = model
        self.active_model = tag
        
        logger.info(f"Model version {tag} saved")
        return tag
    
    def load_version(self, tag: str) -> EnsembleModel:
        """Load specific model version"""
        version_path = os.path.join(self.base_path, tag)
        model = EnsembleModel(version=tag)
        model.load(version_path)
        
        self.models[tag] = model
        self.active_model = tag
        
        logger.info(f"Model version {tag} loaded")
        return model
    
    def get_active_model(self) -> Optional[EnsembleModel]:
        """Get currently active model"""
        if self.active_model and self.active_model in self.models:
            return self.models[self.active_model]
        return None
    
    def list_versions(self) -> List[str]:
        """List all available model versions"""
        return [d for d in os.listdir(self.base_path) 
               if os.path.isdir(os.path.join(self.base_path, d))]


if __name__ == "__main__":
    # Example
    ensemble = EnsembleModel()
    
    # Train XGBoost on dummy data
    X_train = np.random.randn(500, 30)  # 30 technical indicators
    y_train = np.random.randint(0, 3, 500)
    
    ensemble.train_xgboost(X_train, y_train)
    
    logger.info("Ensemble model ready for deployment")
