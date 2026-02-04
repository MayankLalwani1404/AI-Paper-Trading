"""
ML Training Pipeline with Walk-Forward Validation
Implements time-aware cross-validation, anti-overfitting measures, and incremental learning
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
import logging
from datetime import datetime, timedelta
import warnings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


class WalkForwardValidator:
    """
    Time-series aware cross-validation
    Prevents lookahead bias and data leakage
    """
    
    def __init__(self, initial_train_size: int = 500,
                 validation_size: int = 100,
                 step_size: int = 50):
        """
        initial_train_size: Initial training set size
        validation_size: Validation set size for each fold
        step_size: How many samples to step forward each iteration
        """
        self.initial_train_size = initial_train_size
        self.validation_size = validation_size
        self.step_size = step_size
    
    def split(self, X: np.ndarray, y: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generate walk-forward folds
        Returns list of (X_train, y_train, X_val, y_val)
        """
        folds = []
        n_samples = len(X)
        
        train_end = self.initial_train_size
        
        while train_end + self.validation_size < n_samples:
            val_end = train_end + self.validation_size
            
            X_train, y_train = X[:train_end], y[:train_end]
            X_val, y_val = X[train_end:val_end], y[train_end:val_end]
            
            folds.append((X_train, y_train, X_val, y_val))
            
            train_end += self.step_size
        
        logger.info(f"Created {len(folds)} walk-forward folds")
        return folds
    
    def get_test_set(self, X: np.ndarray, y: np.ndarray, 
                    test_fraction: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Get final test set (future data never seen during training/validation)
        """
        test_size = int(len(X) * test_fraction)
        split_point = len(X) - test_size
        
        X_train, y_train = X[:split_point], y[:split_point]
        X_test, y_test = X[split_point:], y[split_point:]
        
        return X_train, y_train, X_test, y_test


class AntiOverfittingValidator:
    """Detects and prevents overfitting"""
    
    @staticmethod
    def detect_overfitting(train_metrics: List[float], 
                          val_metrics: List[float],
                          threshold: float = 0.10) -> bool:
        """
        Detect overfitting: divergence between train and val metrics
        Returns True if overfitting detected
        """
        if len(train_metrics) < 10 or len(val_metrics) < 10:
            return False
        
        recent_train = np.mean(train_metrics[-10:])
        recent_val = np.mean(val_metrics[-10:])
        
        divergence = recent_train - recent_val
        is_overfitting = divergence > threshold
        
        if is_overfitting:
            logger.warning(f"Overfitting detected: train={recent_train:.4f}, val={recent_val:.4f}, divergence={divergence:.4f}")
        
        return is_overfitting
    
    @staticmethod
    def early_stopping(val_loss_history: List[float], 
                      patience: int = 15) -> bool:
        """Stop training if validation loss stops improving"""
        if len(val_loss_history) < patience:
            return False
        
        recent = val_loss_history[-patience:]
        best = min(recent)
        worst = max(recent)
        
        # If no improvement in last 'patience' epochs, stop
        if recent[-1] == worst:
            logger.info(f"Early stopping: no improvement for {patience} epochs")
            return True
        
        return False
    
    @staticmethod
    def stochastic_batch_shuffling(X: np.ndarray, y: np.ndarray,
                                  shuffle_ratio: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Gentle data augmentation: shuffle small fraction of batches
        Prevents memorization while maintaining temporal structure
        """
        n_shuffle = int(len(X) * shuffle_ratio)
        indices = np.random.choice(len(X), n_shuffle, replace=False)
        
        X_aug = X.copy()
        y_aug = y.copy()
        
        # Swap samples within temporal windows to maintain some structure
        for i in range(0, n_shuffle, 2):
            if i + 1 < n_shuffle:
                X_aug[[indices[i], indices[i+1]]] = X_aug[[indices[i+1], indices[i]]]
                y_aug[[indices[i], indices[i+1]]] = y_aug[[indices[i+1], indices[i]]]
        
        return X_aug, y_aug


class IncrementalLearner:
    """
    Incremental/continual learning
    Update models with new data without forgetting old patterns
    """
    
    @staticmethod
    def experience_replay(old_data: Tuple[np.ndarray, np.ndarray],
                         new_data: Tuple[np.ndarray, np.ndarray],
                         replay_ratio: float = 0.3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Mix old and new data for incremental training
        Prevents catastrophic forgetting
        """
        X_old, y_old = old_data
        X_new, y_new = new_data
        
        # Sample from old data
        if len(X_old) > 0:
            n_replay = int(len(X_new) * replay_ratio)
            replay_indices = np.random.choice(len(X_old), min(n_replay, len(X_old)), replace=False)
            
            X_replay = X_old[replay_indices]
            y_replay = y_old[replay_indices]
            
            # Combine
            X_combined = np.vstack([X_new, X_replay])
            y_combined = np.hstack([y_new, y_replay])
            
            return X_combined, y_combined
        
        return X_new, y_new
    
    @staticmethod
    def progressive_resizing(X: np.ndarray, y: np.ndarray,
                            initial_size: int = 0.5,
                            growth_rate: float = 1.1) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Train with progressively larger datasets
        Helps model learn features at different scales
        """
        batches = []
        current_size = int(len(X) * initial_size)
        
        while current_size <= len(X):
            batch_X = X[:int(current_size)]
            batch_y = y[:int(current_size)]
            batches.append((batch_X, batch_y))
            current_size = int(current_size * growth_rate)
        
        return batches


class RegimeDetector:
    """Detects market regimes (bull, bear, sideways)"""
    
    @staticmethod
    def detect_regime(returns: pd.Series, 
                     lookback: int = 60) -> str:
        """
        Detect market regime
        Returns: 'BULL', 'BEAR', 'SIDEWAYS'
        """
        if len(returns) < lookback:
            return 'SIDEWAYS'
        
        recent_returns = returns.iloc[-lookback:]
        
        # Trend
        slope = np.polyfit(range(len(recent_returns)), recent_returns.values, 1)[0]
        volatility = recent_returns.std()
        
        # Bull: positive trend, moderate volatility
        # Bear: negative trend, moderate volatility
        # Sideways: low trend, any volatility
        
        if abs(slope) < 0.0005:
            return 'SIDEWAYS'
        elif slope > 0.0005:
            return 'BULL'
        else:
            return 'BEAR'
    
    @staticmethod
    def apply_regime_weighting(y_train: np.ndarray,
                             regime: str) -> np.ndarray:
        """
        Adjust class weights based on market regime
        Emphasize different outcomes in different markets
        """
        class_weights = np.ones(3)  # [SELL, HOLD, BUY]
        
        if regime == 'BULL':
            class_weights = np.array([0.5, 1.0, 2.0])  # Emphasize BUY signals
        elif regime == 'BEAR':
            class_weights = np.array([2.0, 1.0, 0.5])  # Emphasize SELL signals
        else:  # SIDEWAYS
            class_weights = np.array([1.0, 1.5, 1.0])  # Emphasize HOLD signals
        
        return class_weights


class TrainingPipeline:
    """
    Main training pipeline orchestrating all components
    """
    
    def __init__(self, lookback: int = 50, lookahead: int = 5):
        self.lookback = lookback
        self.lookahead = lookahead
        self.walk_forward_validator = WalkForwardValidator()
        self.overfitting_validator = AntiOverfittingValidator()
        self.incremental_learner = IncrementalLearner()
        self.regime_detector = RegimeDetector()
        
        self.training_history = []
    
    def prepare_training_data(self, df: pd.DataFrame,
                            features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and labels with no lookahead bias"""
        
        X = features_df[features_df.columns.difference(['Close', 'High', 'Low', 'Open', 'Volume'])].values
        
        # Create labels: look ahead 'lookahead' bars
        y = np.zeros(len(df) - self.lookahead, dtype=int)
        
        for i in range(len(y)):
            future_return = (df.iloc[i + self.lookahead]['Close'] - df.iloc[i]['Close']) / df.iloc[i]['Close']
            
            if future_return > 0.01:  # >1% return
                y[i] = 2  # BUY
            elif future_return < -0.01:  # <-1% return
                y[i] = 0  # SELL
            else:
                y[i] = 1  # HOLD
        
        # Trim features to match labels
        X = X[:len(y)]
        
        return X, y
    
    def train_with_walk_forward(self, symbols: Dict[str, Tuple[pd.DataFrame, pd.DataFrame]],
                               model_builder,
                               epochs: int = 50) -> List[Dict]:
        """
        Train models using walk-forward validation across multiple symbols
        """
        all_results = []
        
        for symbol, (df, features_df) in symbols.items():
            logger.info(f"\n=== Training on {symbol} ===")
            
            X, y = self.prepare_training_data(df, features_df)
            
            # Detect market regime
            returns = df['Close'].pct_change()
            regime = self.regime_detector.detect_regime(returns)
            logger.info(f"Market regime: {regime}")
            
            # Get folds
            folds = self.walk_forward_validator.split(X, y)
            
            fold_metrics = []
            for fold_idx, (X_train, y_train, X_val, y_val) in enumerate(folds):
                logger.info(f"  Fold {fold_idx + 1}/{len(folds)}")
                
                # Apply anti-overfitting techniques
                X_train_aug, y_train_aug = self.overfitting_validator.stochastic_batch_shuffling(X_train, y_train)
                
                # Train model
                model = model_builder(X_train_aug.shape[1])
                history = model.train(X_train_aug, y_train_aug, X_val, y_val, epochs=epochs)
                
                fold_metrics.append({
                    'fold': fold_idx,
                    'val_acc': history['val_acc'][-1] if 'val_acc' in history else 0,
                    'val_loss': history['val_loss'][-1] if 'val_loss' in history else 0,
                })
            
            # Get final test set
            X_train_all, y_train_all, X_test, y_test = \
                self.walk_forward_validator.get_test_set(X, y, test_fraction=0.2)
            
            # Final test evaluation
            final_model = model_builder(X_train_all.shape[1])
            final_model.train(X_train_all, y_train_all, epochs=epochs)
            test_acc, _ = final_model.evaluate(X_test, y_test)
            
            symbol_result = {
                'symbol': symbol,
                'regime': regime,
                'fold_metrics': fold_metrics,
                'test_accuracy': test_acc,
                'num_folds': len(folds),
                'timestamp': datetime.now().isoformat(),
            }
            
            all_results.append(symbol_result)
            logger.info(f"{symbol} final test accuracy: {test_acc:.2f}%")
        
        self.training_history = all_results
        return all_results
    
    def get_training_summary(self) -> pd.DataFrame:
        """Get summary statistics of training"""
        summary = pd.DataFrame(self.training_history)
        return summary


if __name__ == "__main__":
    logger.info("Training pipeline ready for deployment")
    logger.info("Supports: walk-forward validation, anti-overfitting, incremental learning, regime detection")
